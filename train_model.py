"""
Phase 2: ML Pipeline - Customer Churn Prediction Model
Train a Random Forest classifier to predict customer churn
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score
import joblib
import json
from datetime import datetime

# ============================================
# 1. DATABASE CONNECTION & DATA EXTRACTION
# ============================================

def load_data_from_db():
    """Load preprocessed features from PostgreSQL"""
    print("Connecting to database...")
    
    # Update with your PostgreSQL credentials
    engine = create_engine('postgresql://postgres:learn@localhost/churn_db')
    
    # Load ML-ready features from the view we created in Phase 1
    query = "SELECT * FROM ml_features"
    df = pd.read_sql(query, engine)
    
    print(f"✓ Loaded {len(df)} records from database")
    print(f"✓ Features: {df.shape[1]} columns")
    print(f"✓ Churn rate: {df['churned'].mean():.2%}")
    
    return df

# ============================================
# 2. DATA PREPROCESSING
# ============================================

def preprocess_data(df):
    """Prepare data for modeling"""
    print("\nPreprocessing data...")
    
    # Separate features and target
    X = df.drop(['customer_id', 'churned'], axis=1)
    y = df['churned']
    
    # Handle any remaining nulls (if any)
    X = X.fillna(0)
    
    print(f"✓ Feature matrix shape: {X.shape}")
    print(f"✓ Target distribution:")
    print(f"  - No churn (0): {(y==0).sum()} ({(y==0).mean():.1%})")
    print(f"  - Churned (1): {(y==1).sum()} ({(y==1).mean():.1%})")
    
    return X, y

# ============================================
# 3. TRAIN-TEST SPLIT & SCALING
# ============================================

def split_and_scale(X, y, test_size=0.2, random_state=42):
    """Split data and scale features"""
    print("\nSplitting and scaling data...")
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    # Scale features (important for some algorithms, good practice)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Convert back to DataFrame to preserve column names
    X_train_scaled = pd.DataFrame(X_train_scaled, columns=X.columns, index=X_train.index)
    X_test_scaled = pd.DataFrame(X_test_scaled, columns=X.columns, index=X_test.index)
    
    print(f"✓ Training set: {X_train_scaled.shape[0]} samples")
    print(f"✓ Test set: {X_test_scaled.shape[0]} samples")
    
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler

# ============================================
# 4. MODEL TRAINING
# ============================================

def train_model(X_train, y_train):
    """Train Random Forest classifier"""
    print("\nTraining Random Forest model...")
    
    # Initialize model with good default parameters
    model = RandomForestClassifier(
        n_estimators=100,        # Number of trees
        max_depth=10,            # Prevent overfitting
        min_samples_split=20,    # Minimum samples to split a node
        min_samples_leaf=10,     # Minimum samples in leaf node
        random_state=42,
        n_jobs=-1,               # Use all CPU cores
        class_weight='balanced'  # Handle class imbalance
    )
    
    # Train
    model.fit(X_train, y_train)
    
    print(f"✓ Model trained successfully")
    print(f"✓ Number of trees: {model.n_estimators}")
    print(f"✓ Feature importance calculated")
    
    return model

# ============================================
# 5. MODEL EVALUATION
# ============================================

def evaluate_model(model, X_test, y_test, X_train, y_train):
    """Evaluate model performance"""
    print("\n" + "="*50)
    print("MODEL EVALUATION")
    print("="*50)
    
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Training accuracy
    train_accuracy = model.score(X_train, y_train)
    test_accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nAccuracy:")
    print(f"  Training: {train_accuracy:.4f}")
    print(f"  Test:     {test_accuracy:.4f}")
    
    if train_accuracy - test_accuracy > 0.1:
        print("  ⚠ Warning: Potential overfitting detected")
    
    # ROC AUC Score
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    print(f"\nROC AUC Score: {roc_auc:.4f}")
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    print(f"\nConfusion Matrix:")
    print(f"                Predicted")
    print(f"              No Churn  Churn")
    print(f"Actual No     {cm[0,0]:6d}   {cm[0,1]:6d}")
    print(f"       Churn  {cm[1,0]:6d}   {cm[1,1]:6d}")
    
    # Classification Report
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['No Churn', 'Churn']))
    
    # Feature Importance
    feature_importance = pd.DataFrame({
        'feature': X_test.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nTop 10 Most Important Features:")
    for idx, row in feature_importance.head(10).iterrows():
        print(f"  {row['feature']:30s} {row['importance']:.4f}")
    
    # Store metrics
    metrics = {
        'train_accuracy': float(train_accuracy),
        'test_accuracy': float(test_accuracy),
        'roc_auc': float(roc_auc),
        'confusion_matrix': cm.tolist(),
        'feature_importance': feature_importance.to_dict('records'),
        'timestamp': datetime.now().isoformat()
    }
    
    return metrics, feature_importance

# ============================================
# 6. SAVE MODEL & ARTIFACTS
# ============================================

def save_model_artifacts(model, scaler, metrics, feature_importance):
    """Save trained model and metadata"""
    print("\nSaving model artifacts...")
    
    # Save model
    joblib.dump(model, 'churn_model.pkl')
    print("✓ Model saved: churn_model.pkl")
    
    # Save scaler
    joblib.dump(scaler, 'scaler.pkl')
    print("✓ Scaler saved: scaler.pkl")
    
    # Save metrics
    with open('model_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    print("✓ Metrics saved: model_metrics.json")
    
    # Save feature importance
    feature_importance.to_csv('feature_importance.csv', index=False)
    print("✓ Feature importance saved: feature_importance.csv")

# ============================================
# 7. MAIN PIPELINE
# ============================================

def main():
    """Run the complete ML pipeline"""
    print("="*50)
    print("PHASE 2: ML PIPELINE - CHURN PREDICTION")
    print("="*50)
    
    try:
        # Step 1: Load data
        df = load_data_from_db()
        
        # Step 2: Preprocess
        X, y = preprocess_data(df)
        
        # Step 3: Split and scale
        X_train, X_test, y_train, y_test, scaler = split_and_scale(X, y)
        
        # Step 4: Train model
        model = train_model(X_train, y_train)
        
        # Step 5: Evaluate
        metrics, feature_importance = evaluate_model(model, X_test, y_test, X_train, y_train)
        
        # Step 6: Save artifacts
        save_model_artifacts(model, scaler, metrics, feature_importance)
        
        print("\n" + "="*50)
        print("✓ PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*50)
        print("\nNext Steps:")
        print("1. Review model_metrics.json for detailed performance")
        print("2. Check feature_importance.csv to understand key drivers")
        print("3. Move to Phase 3 to build the dashboard")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
