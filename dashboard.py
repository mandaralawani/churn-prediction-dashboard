"""
Phase 3: Interactive Dashboard - Customer Churn Prediction
Streamlit dashboard for visualizing model performance and making predictions
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import joblib
import json

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="Churn Prediction Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# LOAD ARTIFACTS
# ============================================

@st.cache_resource
def load_model_artifacts():
    """Load trained model and associated artifacts"""
    try:
        model = joblib.load('churn_model.pkl')
        scaler = joblib.load('scaler.pkl')
        
        with open('model_metrics.json', 'r') as f:
            metrics = json.load(f)
        
        feature_importance = pd.read_csv('feature_importance.csv')
        
        return model, scaler, metrics, feature_importance
    except FileNotFoundError as e:
        st.error(f"⚠️ Model artifacts not found. Please run Phase 2 (train_model.py) first.")
        st.stop()

@st.cache_data
def load_data_from_db():
    """Load customer data from PostgreSQL"""
    try:
        # Update with your credentials
        engine = create_engine('postgresql://postgres:learn@localhost/churn_db')
        
        # Load raw customer data
        query = "SELECT * FROM customers LIMIT 1000"
        df_customers = pd.read_sql(query, engine)
        
        # Load ML features
        query_ml = "SELECT * FROM ml_features"
        df_ml = pd.read_sql(query_ml, engine)
        
        return df_customers, df_ml
    except Exception as e:
        st.error(f"⚠️ Database connection failed: {e}")
        st.info("Make sure PostgreSQL is running and credentials are correct.")
        st.stop()

# ============================================
# LOAD DATA
# ============================================

model, scaler, metrics, feature_importance = load_model_artifacts()
df_customers, df_ml = load_data_from_db()

# ============================================
# SIDEBAR
# ============================================

st.sidebar.title("📊 Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["📈 Overview", "🎯 Model Performance", "🔮 Make Prediction", "👥 Customer Segments"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "This dashboard visualizes customer churn predictions using "
    "a Random Forest model trained on customer behavior data."
)

# ============================================
# PAGE 1: OVERVIEW
# ============================================

if page == "📈 Overview":
    st.title("📈 Customer Churn Analytics Dashboard")
    st.markdown("---")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_customers = len(df_customers)
    churned_customers = df_customers['churned'].sum()
    churn_rate = churned_customers / total_customers * 100
    avg_monthly_revenue = df_customers['monthly_charges'].mean()
    
    with col1:
        st.metric("Total Customers", f"{total_customers:,}")
    
    with col2:
        st.metric("Churned Customers", f"{churned_customers:,}")
    
    with col3:
        st.metric("Churn Rate", f"{churn_rate:.1f}%")
    
    with col4:
        st.metric("Avg Monthly Revenue", f"${avg_monthly_revenue:.2f}")
    
    st.markdown("---")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Churn by Contract Type")
        churn_by_contract = df_customers.groupby('contract_type')['churned'].agg(['sum', 'count'])
        churn_by_contract['rate'] = (churn_by_contract['sum'] / churn_by_contract['count'] * 100).round(2)
        
        fig = px.bar(
            churn_by_contract.reset_index(),
            x='contract_type',
            y='rate',
            title='Churn Rate by Contract Type',
            labels={'rate': 'Churn Rate (%)', 'contract_type': 'Contract Type'},
            color='rate',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Churn by Payment Method")
        churn_by_payment = df_customers.groupby('payment_method')['churned'].agg(['sum', 'count'])
        churn_by_payment['rate'] = (churn_by_payment['sum'] / churn_by_payment['count'] * 100).round(2)
        
        fig = px.bar(
            churn_by_payment.reset_index(),
            x='payment_method',
            y='rate',
            title='Churn Rate by Payment Method',
            labels={'rate': 'Churn Rate (%)', 'payment_method': 'Payment Method'},
            color='rate',
            color_continuous_scale='Oranges'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Revenue Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Monthly Charges Distribution")
        fig = px.histogram(
            df_customers,
            x='monthly_charges',
            color='churned',
            title='Monthly Charges by Churn Status',
            labels={'monthly_charges': 'Monthly Charges ($)', 'churned': 'Churned'},
            barmode='overlay',
            opacity=0.7
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Tenure Distribution")
        fig = px.histogram(
            df_customers,
            x='tenure',
            color='churned',
            title='Customer Tenure by Churn Status',
            labels={'tenure': 'Tenure (months)', 'churned': 'Churned'},
            barmode='overlay',
            opacity=0.7
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================
# PAGE 2: MODEL PERFORMANCE
# ============================================

elif page == "🎯 Model Performance":
    st.title("🎯 Model Performance Metrics")
    st.markdown("---")
    
    # Model Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Test Accuracy", f"{metrics['test_accuracy']:.2%}")
    
    with col2:
        st.metric("ROC AUC Score", f"{metrics['roc_auc']:.4f}")
    
    with col3:
        train_test_gap = metrics['train_accuracy'] - metrics['test_accuracy']
        st.metric("Train-Test Gap", f"{train_test_gap:.2%}")
    
    st.markdown("---")
    
    # Confusion Matrix
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Confusion Matrix")
        cm = np.array(metrics['confusion_matrix'])
        
        fig = go.Figure(data=go.Heatmap(
            z=cm,
            x=['Predicted No Churn', 'Predicted Churn'],
            y=['Actual No Churn', 'Actual Churn'],
            colorscale='Blues',
            text=cm,
            texttemplate='%{text}',
            textfont={"size": 20}
        ))
        
        fig.update_layout(
            title='Confusion Matrix',
            xaxis_title='Predicted',
            yaxis_title='Actual'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate additional metrics from confusion matrix
        tn, fp, fn, tp = cm.ravel()
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1 = 2 * (precision * recall) / (precision + recall)
        
        st.markdown(f"""
        **Derived Metrics:**
        - **Precision**: {precision:.2%} (of predicted churns, how many actually churned)
        - **Recall**: {recall:.2%} (of actual churns, how many we caught)
        - **F1-Score**: {f1:.2%} (harmonic mean of precision and recall)
        """)
    
    with col2:
        st.subheader("Feature Importance")
        
        # Top 15 features
        top_features = feature_importance.head(15)
        
        fig = px.bar(
            top_features,
            x='importance',
            y='feature',
            orientation='h',
            title='Top 15 Most Important Features',
            labels={'importance': 'Importance Score', 'feature': 'Feature'},
            color='importance',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Feature Importance Table
    st.markdown("---")
    st.subheader("All Feature Importances")
    st.dataframe(
        feature_importance.style.background_gradient(subset=['importance'], cmap='YlOrRd'),
        use_container_width=True
    )

# ============================================
# PAGE 3: MAKE PREDICTION
# ============================================

elif page == "🔮 Make Prediction":
    st.title("🔮 Predict Customer Churn")
    st.markdown("Enter customer details to predict churn probability")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Customer Information")
        
        tenure = st.slider("Tenure (months)", 0, 72, 12)
        monthly_charges = st.slider("Monthly Charges ($)", 20.0, 120.0, 70.0)
        total_charges = st.number_input("Total Charges ($)", 0.0, 10000.0, tenure * monthly_charges)
        
        contract_type = st.selectbox(
            "Contract Type",
            ["Month-to-month", "One year", "Two year"]
        )
        
        payment_method = st.selectbox(
            "Payment Method",
            ["Electronic check", "Mailed check", "Bank transfer", "Credit card"]
        )
    
    with col2:
        st.subheader("Services")
        
        has_fiber = st.checkbox("Fiber Optic Internet")
        has_online_security = st.checkbox("Online Security")
        has_tech_support = st.checkbox("Tech Support")
        has_streaming = st.checkbox("Streaming TV")
        paperless_billing = st.checkbox("Paperless Billing")
    
    # Create feature vector
    if st.button("🔮 Predict Churn", type="primary"):
        # Encode features (match ml_features view structure)
        features = {
            'tenure': tenure,
            'monthly_charges': monthly_charges,
            'total_charges': total_charges,
            'is_monthly_contract': 1 if contract_type == 'Month-to-month' else 0,
            'is_yearly_contract': 1 if contract_type == 'One year' else 0,
            'is_two_year_contract': 1 if contract_type == 'Two year' else 0,
            'payment_electronic_check': 1 if payment_method == 'Electronic check' else 0,
            'payment_bank_transfer': 1 if payment_method == 'Bank transfer' else 0,
            'payment_credit_card': 1 if payment_method == 'Credit card' else 0,
            'has_fiber': 1 if has_fiber else 0,
            'has_online_security': 1 if has_online_security else 0,
            'has_tech_support': 1 if has_tech_support else 0,
            'has_streaming': 1 if has_streaming else 0,
            'paperless_billing': 1 if paperless_billing else 0,
            'avg_monthly_spend': total_charges / tenure if tenure > 0 else 0,
            'is_new_customer': 1 if tenure < 12 else 0,
            'is_high_spender': 1 if monthly_charges > 80 else 0
        }
        
        # Convert to DataFrame
        X_input = pd.DataFrame([features])
        
        # Scale features
        X_scaled = scaler.transform(X_input)
        
        # Make prediction
        prediction = model.predict(X_scaled)[0]
        probability = model.predict_proba(X_scaled)[0]
        
        # Display results
        st.markdown("---")
        st.subheader("Prediction Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if prediction == 1:
                st.error("⚠️ HIGH RISK - Likely to Churn")
            else:
                st.success("✅ LOW RISK - Unlikely to Churn")
        
        with col2:
            st.metric("Churn Probability", f"{probability[1]:.1%}")
        
        with col3:
            st.metric("Retention Probability", f"{probability[0]:.1%}")
        
        # Risk gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=probability[1] * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Churn Risk Score"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkred"},
                'steps': [
                    {'range': [0, 33], 'color': "lightgreen"},
                    {'range': [33, 66], 'color': "yellow"},
                    {'range': [66, 100], 'color': "lightcoral"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 50
                }
            }
        ))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Recommendations
        st.subheader("💡 Retention Recommendations")
        
        if prediction == 1:
            recommendations = []
            
            if contract_type == "Month-to-month":
                recommendations.append("✅ Offer long-term contract discount (1-2 year)")
            
            if payment_method == "Electronic check":
                recommendations.append("✅ Encourage automatic payment via bank transfer or credit card")
            
            if tenure < 12:
                recommendations.append("✅ Provide onboarding support and early engagement incentives")
            
            if not has_online_security:
                recommendations.append("✅ Offer complimentary online security for 3 months")
            
            if not has_tech_support:
                recommendations.append("✅ Provide free tech support trial")
            
            if monthly_charges > 80:
                recommendations.append("✅ Review pricing and offer loyalty discount")
            
            if recommendations:
                for rec in recommendations:
                    st.markdown(rec)
            else:
                st.markdown("✅ Monitor customer engagement and provide proactive support")
        else:
            st.success("✅ Customer is stable. Continue providing excellent service!")

# ============================================
# PAGE 4: CUSTOMER SEGMENTS
# ============================================

elif page == "👥 Customer Segments":
    st.title("👥 Customer Segmentation Analysis")
    st.markdown("---")
    
    # Segment by tenure and revenue
    df_customers['tenure_segment'] = pd.cut(
        df_customers['tenure'],
        bins=[0, 12, 36, 72],
        labels=['New (<1yr)', 'Regular (1-3yr)', 'Loyal (>3yr)']
    )
    
    df_customers['revenue_segment'] = pd.cut(
        df_customers['monthly_charges'],
        bins=[0, 40, 80, 120],
        labels=['Low Value', 'Medium Value', 'High Value']
    )
    
    # Segment Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Churn by Tenure Segment")
        segment_analysis = df_customers.groupby('tenure_segment')['churned'].agg(['sum', 'count', 'mean'])
        segment_analysis.columns = ['Churned', 'Total', 'Churn Rate']
        segment_analysis['Churn Rate'] = (segment_analysis['Churn Rate'] * 100).round(2)
        
        fig = px.bar(
            segment_analysis.reset_index(),
            x='tenure_segment',
            y='Churn Rate',
            title='Churn Rate by Tenure Segment',
            labels={'Churn Rate': 'Churn Rate (%)', 'tenure_segment': 'Segment'},
            color='Churn Rate',
            color_continuous_scale='RdYlGn_r',
            text='Churn Rate'
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(segment_analysis, use_container_width=True)
    
    with col2:
        st.subheader("Churn by Revenue Segment")
        revenue_analysis = df_customers.groupby('revenue_segment')['churned'].agg(['sum', 'count', 'mean'])
        revenue_analysis.columns = ['Churned', 'Total', 'Churn Rate']
        revenue_analysis['Churn Rate'] = (revenue_analysis['Churn Rate'] * 100).round(2)
        
        fig = px.bar(
            revenue_analysis.reset_index(),
            x='revenue_segment',
            y='Churn Rate',
            title='Churn Rate by Revenue Segment',
            labels={'Churn Rate': 'Churn Rate (%)', 'revenue_segment': 'Segment'},
            color='Churn Rate',
            color_continuous_scale='RdYlGn_r',
            text='Churn Rate'
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(revenue_analysis, use_container_width=True)
    
    # 2D Segmentation Heatmap
    st.markdown("---")
    st.subheader("Customer Segmentation Matrix")
    
    segment_matrix = pd.crosstab(
        df_customers['tenure_segment'],
        df_customers['revenue_segment'],
        df_customers['churned'],
        aggfunc='mean'
    ) * 100
    
    fig = px.imshow(
        segment_matrix,
        labels=dict(x="Revenue Segment", y="Tenure Segment", color="Churn Rate (%)"),
        x=segment_matrix.columns,
        y=segment_matrix.index,
        color_continuous_scale='RdYlGn_r',
        aspect="auto",
        text_auto='.1f'
    )
    
    fig.update_layout(title="Churn Rate by Customer Segment")
    st.plotly_chart(fig, use_container_width=True)
    
    # High-Risk Customers Table
    st.markdown("---")
    st.subheader("🚨 High-Risk Customers")
    st.markdown("Customers with highest churn probability based on current characteristics")
    
    # Get predictions for all customers
    X_all = df_ml.drop(['customer_id', 'churned'], axis=1)
    X_all_scaled = scaler.transform(X_all)
    churn_probabilities = model.predict_proba(X_all_scaled)[:, 1]
    
    # Add to dataframe
    df_risk = df_customers.copy()
    df_risk['churn_probability'] = churn_probabilities
    
    # Filter high-risk customers (not already churned)
    high_risk = df_risk[
        (df_risk['churned'] == False) & 
        (df_risk['churn_probability'] > 0.6)
    ].sort_values('churn_probability', ascending=False)
    
    # Display top 20
    display_cols = [
        'customer_id', 'tenure', 'contract_type', 'monthly_charges', 
        'payment_method', 'churn_probability'
    ]
    
    high_risk_display = high_risk[display_cols].head(20).copy()
    high_risk_display['churn_probability'] = (high_risk_display['churn_probability'] * 100).round(1)
    high_risk_display = high_risk_display.rename(columns={'churn_probability': 'Risk (%)'})
    
    st.dataframe(
        high_risk_display.style.background_gradient(subset=['Risk (%)'], cmap='Reds'),
        use_container_width=True,
        height=400
    )
    
    st.info(f"📊 Found {len(high_risk)} high-risk customers (>60% churn probability)")
