# Windows Quick Start Guide

## Prerequisites
- Windows 10/11
- Python 3.8+ installed
- PostgreSQL 14+ installed

## One-Time Setup

### 1. Install PostgreSQL
- Download: https://www.postgresql.org/download/windows/
- During install, remember your postgres password
- Default port: 5432

### 2. Install Python Packages
Open PowerShell or Command Prompt:
```cmd
pip install pandas numpy sqlalchemy psycopg2-binary streamlit scikit-learn joblib
```

### 3. Create Database
```cmd
psql -U postgres -c "CREATE DATABASE churn_db;"
```

## Running Phase 1

### Generate Data
```cmd
python generate_data.py
```

**Important:** Edit `generate_data.py` line 45 with your postgres password:
```python
engine = create_engine('postgresql://postgres:YOUR_PASSWORD@localhost/churn_db')
```

### Load SQL Features
```cmd
psql -U postgres -d churn_db -f feature_engineering.sql
```

### Verify Data
```cmd
psql -U postgres -d churn_db -c "SELECT COUNT(*) FROM customers;"
```

## Common Issues

### "psql is not recognized"
Add to PATH: `C:\Program Files\PostgreSQL\14\bin`
Then restart your terminal.

### "password authentication failed"
Check your postgres password in the connection string.

### "pip install fails"
Try running PowerShell/CMD as Administrator.

### Port 5432 already in use
Another PostgreSQL instance is running. Check Services (services.msc).

## File Structure
```
project/
├── generate_data.py          # Data generation script
├── feature_engineering.sql   # SQL queries
├── README_phase1.md          # Detailed instructions
└── customers_data.csv        # Backup if DB fails
```

## Next Steps
Once Phase 1 completes successfully:
1. Verify data: `SELECT * FROM ml_features LIMIT 5;`
2. Move to Phase 2: ML Pipeline (train_model.py)
3. Phase 3: Dashboard (dashboard.py)
