# Phase 3: Interactive Dashboard with Streamlit

## Prerequisites
- Completed Phase 1 (database setup)
- Completed Phase 2 (trained model artifacts)
- Model files in same directory:
  - `churn_model.pkl`
  - `scaler.pkl`
  - `model_metrics.json`
  - `feature_importance.csv`

## Installation

```cmd
pip install streamlit plotly pandas numpy sqlalchemy psycopg2-binary joblib
```

## Configuration

### Step 1: Update Database Credentials
Edit `dashboard.py` line 54:
```python
engine = create_engine('postgresql://postgres:YOUR_PASSWORD@localhost/churn_db')
```

### Step 2: Ensure Model Files Exist
Run Phase 2 first if you haven't:
```cmd
python train_model.py
```

This creates:
- ✅ churn_model.pkl
- ✅ scaler.pkl
- ✅ model_metrics.json
- ✅ feature_importance.csv

## Running the Dashboard

```cmd
streamlit run dashboard.py
```

The dashboard will open automatically in your browser at:
**http://localhost:8501**

## Dashboard Pages

### 📈 Overview
**Business Intelligence Dashboard**
- Key metrics (total customers, churn rate, revenue)
- Churn rate by contract type
- Churn rate by payment method
- Monthly charges distribution
- Tenure distribution
- Interactive visualizations

### 🎯 Model Performance
**ML Model Evaluation**
- Test accuracy and ROC AUC score
- Confusion matrix visualization
- Precision, Recall, F1-Score
- Feature importance rankings (top 15)
- Complete feature importance table

### 🔮 Make Prediction
**Real-time Churn Prediction**
- Input customer details via sliders and dropdowns
- Predict churn probability
- Visual risk gauge (0-100%)
- Personalized retention recommendations
- Actionable insights based on customer profile

**Input Fields:**
- Tenure (months)
- Monthly charges
- Total charges
- Contract type
- Payment method
- Services (fiber, security, support, streaming)

**Output:**
- Risk classification (High/Low)
- Churn probability percentage
- Retention probability
- Visual gauge chart
- Specific recommendations

### 👥 Customer Segments
**Segmentation Analysis**
- Churn rate by tenure segment (New/Regular/Loyal)
- Churn rate by revenue segment (Low/Medium/High)
- 2D segmentation heatmap
- High-risk customer list (>60% churn probability)
- Exportable customer data

## Features

### Interactive Visualizations
- Bar charts (Plotly)
- Histograms
- Heatmaps
- Gauge charts
- Color-coded tables

### Real-time Analysis
- Live predictions
- Dynamic filtering
- Responsive design

### Data Caching
- Fast page loads with `@st.cache_resource`
- Efficient database queries with `@st.cache_data`

## Sample Screenshots

### Overview Page
```
┌──────────────────────────────────────────────────┐
│  Total Customers    Churned    Churn Rate   Avg  │
│      1,000            352        35.2%     $70.45 │
└──────────────────────────────────────────────────┘

[Bar Chart: Churn by Contract]  [Bar Chart: Churn by Payment]
[Histogram: Monthly Charges]    [Histogram: Tenure]
```

### Make Prediction
```
Customer Information              Services
┌─────────────────────┐         ┌──────────────────┐
│ Tenure: 12 months   │         │ ☑ Fiber Optic    │
│ Monthly: $70        │         │ ☐ Online Security│
│ Contract: Month-to- │         │ ☐ Tech Support   │
│          month      │         │ ☑ Streaming TV   │
│ Payment: E-check    │         │ ☑ Paperless Bill │
└─────────────────────┘         └──────────────────┘

         [🔮 Predict Churn]

Results:
⚠️ HIGH RISK - Likely to Churn
Churn Probability: 72.5%

[Gauge Chart showing 72.5]

💡 Recommendations:
✅ Offer long-term contract discount
✅ Encourage automatic payment
✅ Offer complimentary online security
```

## Troubleshooting

### Dashboard won't start
```cmd
# Check if Streamlit is installed
pip show streamlit

# Reinstall if needed
pip install streamlit --upgrade
```

### "Model artifacts not found"
```cmd
# Run Phase 2 first
python train_model.py

# Verify files exist
dir churn_model.pkl scaler.pkl model_metrics.json feature_importance.csv
```

### Database connection fails
- Verify PostgreSQL is running: `services.msc` → postgresql
- Check credentials in `dashboard.py` line 54
- Test connection: `psql -U postgres -d churn_db`

### "Port 8501 already in use"
```cmd
# Kill existing Streamlit process
taskkill /F /IM streamlit.exe

# Or use different port
streamlit run dashboard.py --server.port 8502
```

### Dashboard is slow
- Data is cached automatically
- Reduce number of customers loaded (line 55)
- Close other browser tabs

## Customization

### Change Theme
Create `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

### Modify Risk Threshold
Edit line 400 in `dashboard.py`:
```python
high_risk = df_risk[
    (df_risk['churned'] == False) & 
    (df_risk['churn_probability'] > 0.5)  # Change from 0.6 to 0.5
]
```

### Add New Metrics
Add to Overview page:
```python
lifetime_value = (df_customers['tenure'] * df_customers['monthly_charges']).mean()
st.metric("Avg Lifetime Value", f"${lifetime_value:.2f}")
```

## Tips for Presentation

1. **Start with Overview** - Show business context
2. **Model Performance** - Demonstrate accuracy
3. **Live Prediction** - Interactive demo with audience
4. **Customer Segments** - Identify high-risk groups

## Keyboard Shortcuts

- `R` - Rerun the app
- `C` - Clear cache
- `Ctrl+C` - Stop the dashboard

## Next Steps

### Deployment Options
1. **Streamlit Cloud** (Free)
   - Push to GitHub
   - Deploy at share.streamlit.io

2. **Heroku**
   - Requires `Procfile` and `requirements.txt`

3. **Docker**
   - Containerize for enterprise deployment

### Enhancements
- Add time-series predictions
- Email alert system for high-risk customers
- A/B testing for retention strategies
- Integration with CRM systems
- Automated retraining pipeline

## Support

Common issues and solutions:
- **Blank page**: Check browser console (F12)
- **Data not updating**: Press `R` to rerun
- **Slow performance**: Reduce data size or add pagination
