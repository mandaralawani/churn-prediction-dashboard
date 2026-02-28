# Phase 1 Setup Instructions (Windows)

## Step 0: Install PostgreSQL
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Run the installer (PostgreSQL 14 or later recommended)
3. Remember your postgres user password during installation
4. Add PostgreSQL bin directory to PATH (installer usually does this)

## Step 1: Create Database
Open Command Prompt or PowerShell:
```cmd
# Verify PostgreSQL is installed
psql --version

# Create database (enter postgres password when prompted)
psql -U postgres -c "CREATE DATABASE churn_db;"
```

## Step 2: Install Python Dependencies
```cmd
pip install pandas numpy sqlalchemy psycopg2-binary
```

## Step 3: Generate Sample Data
```cmd
python generate_data.py
```

This will:
- Generate 1,000 synthetic customer records
- Calculate realistic churn based on business rules
- Load data into PostgreSQL `churn_db.customers` table
- If DB connection fails, saves to `customers_data.csv`

## Step 4: Run Feature Engineering Queries

Connect to your database:
```cmd
psql -U postgres -d churn_db
```

Then run the SQL file:
```sql
\i feature_engineering.sql
```

**Or** in PowerShell:
```powershell
Get-Content feature_engineering.sql | psql -U postgres -d churn_db
```

### Key Queries to Explore:

**View customer segments:**
```sql
SELECT * FROM customer_segments LIMIT 10;
```

**Check churn rate by contract type:**
```sql
SELECT contract_type, churn_rate_pct 
FROM (
    SELECT contract_type,
           ROUND(100.0 * SUM(CASE WHEN churned THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct
    FROM customers
    GROUP BY contract_type
) t
ORDER BY churn_rate_pct DESC;
```

**Get ML-ready features:**
```sql
SELECT * FROM ml_features LIMIT 5;
```

**Identify high-risk customers:**
```sql
SELECT * FROM high_risk_customers LIMIT 20;
```

## Verify Your Data

```sql
-- Check row count
SELECT COUNT(*) FROM customers;

-- Check churn distribution
SELECT churned, COUNT(*) 
FROM customers 
GROUP BY churned;

-- Sample the data
SELECT * FROM customers LIMIT 5;
```

## Troubleshooting

**If PostgreSQL service won't start:**
```cmd
# Check service status in Services app (Win + R, type services.msc)
# Or restart from command prompt (as Administrator):
net stop postgresql-x64-14
net start postgresql-x64-14
```

**If database doesn't exist:**
```cmd
psql -U postgres -c "CREATE DATABASE churn_db;"
```

**If Python libraries missing:**
```cmd
pip install pandas numpy sqlalchemy psycopg2-binary
```

**If psql command not found:**
- Add PostgreSQL bin folder to PATH: `C:\Program Files\PostgreSQL\14\bin`
- Restart Command Prompt after adding to PATH

## Next: Phase 2
Once data is loaded and features are engineered, move to Phase 2 (ML Pipeline) with the `ml_features` view as your training dataset.
