# Installation (Windows):
# pip install pandas numpy sqlalchemy psycopg2-binary

import pandas as pd
import numpy as np
import psycopg2
from sqlalchemy import create_engine

# Generate synthetic customer data
np.random.seed(42)
n_customers = 1000

data = {
    'customer_id': range(1, n_customers + 1),
    'tenure': np.random.randint(1, 72, n_customers),  # months
    'monthly_charges': np.random.uniform(20, 120, n_customers).round(2),
    'total_charges': None,  # Will calculate based on tenure
    'contract_type': np.random.choice(['Month-to-month', 'One year', 'Two year'], n_customers, p=[0.5, 0.3, 0.2]),
    'payment_method': np.random.choice(['Electronic check', 'Mailed check', 'Bank transfer', 'Credit card'], n_customers),
    'internet_service': np.random.choice(['DSL', 'Fiber optic', 'No'], n_customers, p=[0.35, 0.45, 0.2]),
    'online_security': np.random.choice(['Yes', 'No', 'No internet service'], n_customers),
    'tech_support': np.random.choice(['Yes', 'No', 'No internet service'], n_customers),
    'streaming_tv': np.random.choice(['Yes', 'No', 'No internet service'], n_customers),
    'paperless_billing': np.random.choice([True, False], n_customers, p=[0.6, 0.4]),
}

df = pd.DataFrame(data)

# Calculate total charges (tenure * monthly + some variance)
df['total_charges'] = (df['tenure'] * df['monthly_charges'] * np.random.uniform(0.95, 1.05, n_customers)).round(2)

# Generate churn based on business rules (more realistic)
churn_probability = (
    0.1 +  # base rate
    0.3 * (df['contract_type'] == 'Month-to-month').astype(int) +
    0.2 * (df['payment_method'] == 'Electronic check').astype(int) +
    0.15 * (df['tenure'] < 12).astype(int) +
    0.1 * (df['monthly_charges'] > 80).astype(int) -
    0.2 * (df['online_security'] == 'Yes').astype(int) -
    0.15 * (df['tech_support'] == 'Yes').astype(int)
)
churn_probability = np.clip(churn_probability, 0, 0.8)
df['churned'] = (np.random.random(n_customers) < churn_probability).astype(bool)

print(f"Generated {len(df)} customers")
print(f"Churn rate: {df['churned'].mean():.2%}")
print(f"\nFirst 5 rows:")
print(df.head())

# Connect to PostgreSQL and load data
try:
    # Update connection string with your credentials
    # Default Windows: 'postgresql://postgres:YOUR_PASSWORD@localhost/churn_db'
    engine = create_engine('postgresql://postgres:learn@localhost/churn_db')
    
    # Load data into database
    df.to_sql('customers', engine, if_exists='replace', index=False)
    print(f"\n✓ Data loaded to PostgreSQL successfully!")
    
    # Verify
    with engine.connect() as conn:
        result = conn.execute("SELECT COUNT(*) FROM customers")
        count = result.fetchone()[0]
        print(f"✓ Verified: {count} rows in database")
        
except Exception as e:
    print(f"\n⚠ Database connection failed: {e}")
    print("Saving to CSV as backup...")
    df.to_csv('customers_data.csv', index=False)
    print("✓ Data saved to customers_data.csv")
