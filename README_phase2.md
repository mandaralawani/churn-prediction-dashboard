# Phase 2: ML Pipeline - Model Training

## Prerequisites
- Completed Phase 1 (database with ml_features view)
- Python packages installed

## Installation

```cmd
pip install pandas numpy scikit-learn sqlalchemy psycopg2-binary joblib
```

## Running the Pipeline

### Step 1: Update Database Credentials
Edit `train_model.py` line 24:
```python
engine = create_engine('postgresql://postgres:YOUR_PASSWORD@localhost/churn_db')
```

### Step 2: Run Training Script
```cmd
python train_model.py
```

## What the Script Does

### 1. Data Extraction
- Connects to PostgreSQL
- Loads preprocessed features from `ml_features` view
- Displays data summary

### 2. Preprocessing
- Separates features (X) from target (y)
- Handles missing values
- Shows class distribution

### 3. Train-Test Split
- 80% training, 20% testing
- Stratified split (maintains churn ratio)
- StandardScaler for feature normalization

### 4. Model Training
- Random Forest Classifier (100 trees)
- Balanced class weights (handles imbalanced data)
- Prevents overfitting with max_depth=10

### 5. Evaluation
- Accuracy (train & test)
- ROC AUC Score
- Confusion Matrix
- Precision, Recall, F1-Score
- Feature Importance Rankings

### 6. Model Artifacts Saved
- **churn_model.pkl** - Trained model
- **scaler.pkl** - Feature scaler
- **model_metrics.json** - Performance metrics
- **feature_importance.csv** - Feature rankings

## Expected Output

```
==================================================
PHASE 2: ML PIPELINE - CHURN PREDICTION
==================================================
Connecting to database...
✓ Loaded 1000 records from database
✓ Features: 20 columns
✓ Churn rate: 35.20%

Preprocessing data...
✓ Feature matrix shape: (1000, 18)
✓ Target distribution:
  - No churn (0): 648 (64.8%)
  - Churned (1): 352 (35.2%)

Splitting and scaling data...
✓ Training set: 800 samples
✓ Test set: 200 samples

Training Random Forest model...
✓ Model trained successfully
✓ Number of trees: 100
✓ Feature importance calculated

==================================================
MODEL EVALUATION
==================================================

Accuracy:
  Training: 0.8625
  Test:     0.8100

ROC AUC Score: 0.8652

Confusion Matrix:
                Predicted
              No Churn  Churn
Actual No         112     18
       Churn        20     50

Classification Report:
              precision    recall  f1-score   support

    No Churn       0.85      0.86      0.86       130
       Churn       0.74      0.71      0.72        70

    accuracy                           0.81       200
   macro avg       0.79      0.79      0.79       200
weighted avg       0.81      0.81      0.81       200

Top 10 Most Important Features:
  tenure                         0.2150
  total_charges                  0.1842
  monthly_charges                0.1635
  is_monthly_contract            0.0892
  avg_monthly_spend              0.0765
  ...

Saving model artifacts...
✓ Model saved: churn_model.pkl
✓ Scaler saved: scaler.pkl
✓ Metrics saved: model_metrics.json
✓ Feature importance saved: feature_importance.csv

==================================================
✓ PIPELINE COMPLETED SUCCESSFULLY!
==================================================
```

## Understanding the Metrics

### Accuracy
- **Training**: 86% - How well model fits training data
- **Test**: 81% - How well model generalizes to new data
- Gap <10% = Good generalization

### ROC AUC Score
- 0.50 = Random guessing
- 0.70-0.80 = Acceptable
- 0.80-0.90 = Excellent ✓
- 0.90+ = Outstanding

### Confusion Matrix
```
              Predicted
            No Churn  Churn
True No        112      18     ← 18 false positives
     Churn      20      50     ← 20 false negatives
```

### Precision vs Recall
- **Precision**: Of predicted churns, how many actually churned?
- **Recall**: Of actual churns, how many did we catch?
- **F1-Score**: Harmonic mean of both

## Model Tuning (Optional)

If results aren't satisfactory, edit these parameters in `train_model.py`:

```python
RandomForestClassifier(
    n_estimators=200,        # More trees (slower but better)
    max_depth=15,            # Deeper trees (risk overfitting)
    min_samples_split=10,    # Lower = more complex model
    class_weight='balanced'  # Keep for imbalanced data
)
```

## Troubleshooting

**Database connection fails:**
- Verify PostgreSQL is running
- Check credentials in connection string
- Ensure `churn_db` exists

**Low accuracy (<70%):**
- Check data quality in Phase 1
- Try different hyperparameters
- Add more features

**High training accuracy, low test accuracy:**
- Model is overfitting
- Reduce max_depth
- Increase min_samples_split

## Next: Phase 3
Once training completes successfully, proceed to Phase 3 to build an interactive Streamlit dashboard.
