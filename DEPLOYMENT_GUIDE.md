# Streamlit Cloud Deployment Guide

## Complete Step-by-Step Guide to Deploy Your Dashboard

---

## 📋 Prerequisites

Before starting, ensure you have:
- ✅ Completed Phases 1, 2, and 3 locally
- ✅ Model artifacts generated (churn_model.pkl, scaler.pkl, etc.)
- ✅ GitHub account (free)
- ✅ Git installed on Windows

---

## Part 1: Install Git on Windows

### Step 1: Download Git
1. Go to https://git-scm.com/download/win
2. Download "64-bit Git for Windows Setup"
3. Run the installer with default settings

### Step 2: Verify Installation
```cmd
git --version
```
Should show: `git version 2.x.x`

### Step 3: Configure Git
```cmd
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## Part 2: Setup Cloud Database (Required for Deployment)

Your local PostgreSQL won't be accessible from Streamlit Cloud. You need a cloud database.

### Option A: ElephantSQL (Recommended - Free)

1. **Sign up**: https://www.elephantsql.com/
2. **Create Instance**:
   - Click "Create New Instance"
   - Name: `churn-db`
   - Plan: "Tiny Turtle" (Free)
   - Region: Choose closest to you
   - Click "Create Instance"

3. **Get Connection Details**:
   - Click on your instance name
   - Copy the URL (looks like: `postgres://username:password@host/database`)
   - Or copy individual details:
     - Server (host)
     - User & Default database
     - Password

4. **Migrate Your Data**:
   
   **Method 1: Using pg_dump (if you have PostgreSQL tools)**
   ```cmd
   # Export from local database
   pg_dump -U postgres -h localhost churn_db > churn_backup.sql
   
   # Import to ElephantSQL (replace with your URL)
   psql "postgres://username:password@host/database" < churn_backup.sql
   ```
   
   **Method 2: Using Python (easier)**
   Create `migrate_database.py`:
   ```python
   import pandas as pd
   from sqlalchemy import create_engine
   
   # Source (local)
   source_engine = create_engine('postgresql://postgres:YOUR_PASSWORD@localhost/churn_db')
   
   # Destination (ElephantSQL - replace with your URL)
   dest_engine = create_engine('postgresql://username:password@host/database')
   
   # Migrate customers table
   df = pd.read_sql('SELECT * FROM customers', source_engine)
   df.to_sql('customers', dest_engine, if_exists='replace', index=False)
   print(f"✓ Migrated {len(df)} customers")
   
   # Migrate ml_features view (as table)
   df_ml = pd.read_sql('SELECT * FROM ml_features', source_engine)
   df_ml.to_sql('ml_features', dest_engine, if_exists='replace', index=False)
   print(f"✓ Migrated {len(df_ml)} ML features")
   
   print("✓ Database migration complete!")
   ```
   
   Run it:
   ```cmd
   python migrate_database.py
   ```

### Option B: Supabase (Alternative - Free)

1. Sign up: https://supabase.com/
2. Create new project
3. Go to Settings → Database
4. Copy connection string
5. Use same migration script above with Supabase URL

---

## Part 3: Prepare Your Project for GitHub

### Step 1: Create Project Directory
```cmd
# Navigate to your project folder
cd path\to\your\project

# Example:
cd C:\Users\YourName\Documents\churn-prediction
```

### Step 2: Verify Required Files

Your project folder should have:
```
churn-prediction/
├── dashboard_cloud.py          # Main app (use cloud version)
├── churn_model.pkl            # Trained model
├── scaler.pkl                 # Feature scaler
├── model_metrics.json         # Model metrics
├── feature_importance.csv     # Feature rankings
├── requirements.txt           # Python dependencies
├── .gitignore                 # Files to exclude from Git
├── README.md                  # Project description (optional)
└── .streamlit/
    ├── config.toml            # Streamlit config
    └── secrets.toml.template  # Secrets template
```

**IMPORTANT**: Rename `dashboard_cloud.py` to `dashboard.py` before deploying:
```cmd
rename dashboard_cloud.py dashboard.py
```

Or copy it:
```cmd
copy dashboard_cloud.py dashboard.py
```

### Step 3: Create README.md (Optional)
```cmd
# Create a simple README
echo # Customer Churn Prediction Dashboard > README.md
echo ML-powered dashboard to predict and analyze customer churn >> README.md
```

---

## Part 4: Push to GitHub

### Step 1: Initialize Git Repository
```cmd
# Initialize repository
git init

# Add all files
git add .

# Verify what will be committed
git status
```

### Step 2: Make First Commit
```cmd
git commit -m "Initial commit: Churn prediction dashboard"
```

### Step 3: Create GitHub Repository

1. **Go to GitHub**: https://github.com/
2. **Click** the **+** icon (top right) → "New repository"
3. **Fill in details**:
   - Repository name: `churn-prediction-dashboard`
   - Description: "ML dashboard for customer churn prediction"
   - Visibility: **Public** (required for free Streamlit Cloud)
   - **DO NOT** check "Initialize with README" (we already have one)
4. **Click** "Create repository"

### Step 4: Connect Local Repo to GitHub

GitHub will show you commands. Use these:

```cmd
# Add remote (replace YOUR-USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR-USERNAME/churn-prediction-dashboard.git

# Verify remote was added
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

**If prompted for credentials:**
- Username: Your GitHub username
- Password: Use a **Personal Access Token** (not your account password)
  
  **To create a token:**
  1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
  2. Generate new token → Give it a name
  3. Select scopes: `repo` (full control)
  4. Generate token and **copy it** (you won't see it again!)
  5. Use this token as your password

### Step 5: Verify Upload
Go to: `https://github.com/YOUR-USERNAME/churn-prediction-dashboard`

You should see all your files!

---

## Part 5: Deploy on Streamlit Cloud

### Step 1: Sign Up for Streamlit Cloud

1. **Go to**: https://share.streamlit.io/
2. **Click** "Sign up" or "Get started"
3. **Sign in with GitHub** (recommended)
4. **Authorize** Streamlit to access your repositories

### Step 2: Deploy New App

1. **Click** "New app" button
2. **Fill in details**:
   - **Repository**: Select `your-username/churn-prediction-dashboard`
   - **Branch**: `main`
   - **Main file path**: `dashboard.py`
   - **App URL** (optional): Choose a custom subdomain
     - Example: `churn-predictor.streamlit.app`
     - Or auto-generated: `your-username-churn-prediction-dashboard.streamlit.app`

3. **Click** "Advanced settings" (before deploying)

### Step 3: Configure Secrets

This is **CRITICAL** - your database credentials!

In the **Advanced settings** section:

1. Find **"Secrets"** section
2. Paste your database credentials in TOML format:

```toml
[database]
host = "your-elephantsql-host.com"
port = 5432
database = "your_database_name"
user = "your_username"
password = "your_password"
```

**Example with ElephantSQL:**
```toml
[database]
host = "jelani.db.elephantsql.com"
port = 5432
database = "abcdefgh"
user = "abcdefgh"
password = "super_secret_password_here"
```

**Pro tip**: Get this from your ElephantSQL URL:
`postgres://user:password@host:port/database`

3. **Click** "Save"

### Step 4: Deploy!

1. **Click** "Deploy!"
2. **Wait** 2-5 minutes for deployment
   - You'll see logs in real-time
   - Installation of packages
   - Building the app
   - "Your app is live!"

3. **Access your dashboard** at:
   `https://your-app-name.streamlit.app`

---

## Part 6: Verify Deployment

### Test Checklist:
- [ ] Overview page loads with data
- [ ] Charts display correctly
- [ ] Model Performance page shows metrics
- [ ] Make Prediction form works
- [ ] Customer Segments page loads
- [ ] No database connection errors

---

## 🎉 Your Dashboard is Live!

Share your URL with anyone:
`https://your-app-name.streamlit.app`

---

## Part 7: Update Your App (After Changes)

Whenever you make changes locally:

```cmd
# Make your changes to files
# Then:

git add .
git commit -m "Description of changes"
git push origin main
```

**Streamlit Cloud automatically redeploys** when you push to GitHub!

---

## Troubleshooting

### Issue 1: "ModuleNotFoundError"
**Solution**: Check `requirements.txt` has all dependencies
```cmd
# Locally verify it works:
pip install -r requirements.txt
python dashboard.py
```

### Issue 2: "Database connection failed"
**Solutions**:
1. Verify secrets are configured correctly in Streamlit Cloud
2. Check ElephantSQL instance is active
3. Verify database has data (use migration script)
4. Check if firewall/IP restrictions on database

**Test connection from Python:**
```python
from sqlalchemy import create_engine
engine = create_engine('your-elephantsql-url')
print(engine.connect())
```

### Issue 3: "File not found: churn_model.pkl"
**Solution**: Ensure all model files are committed to Git
```cmd
git add churn_model.pkl scaler.pkl model_metrics.json feature_importance.csv
git commit -m "Add model artifacts"
git push origin main
```

### Issue 4: App crashes on startup
**Solution**: Check logs in Streamlit Cloud dashboard
- Click "Manage app" → "Logs"
- Look for specific error messages

### Issue 5: "App quota exceeded"
**Solution**: Free tier limits:
- 1 app
- 1GB memory
- 1 CPU core
- Consider Streamlit Cloud paid plan if needed

---

## Advanced: Custom Domain (Optional)

If you have a custom domain:

1. **Streamlit Cloud Settings** → Your app → "Settings"
2. **Add custom domain**: `dashboard.yourdomain.com`
3. **Add DNS record** at your domain provider:
   ```
   Type: CNAME
   Name: dashboard
   Value: your-app-name.streamlit.app
   ```
4. **Wait** for DNS propagation (5-30 minutes)

---

## Security Best Practices

### ✅ DO:
- Use secrets for database credentials
- Keep `.gitignore` updated
- Use cloud database with SSL
- Regularly update dependencies

### ❌ DON'T:
- Commit passwords or API keys to Git
- Use localhost database URLs in production
- Share your secrets.toml file
- Commit sensitive customer data

---

## Free Tier Limits

**GitHub:**
- Unlimited public repositories
- 500 MB repository size

**Streamlit Cloud Free:**
- 1 app per account
- 1 GB RAM
- 1 CPU core
- Sleep after 7 days of inactivity

**ElephantSQL Free:**
- 20 MB storage
- 5 concurrent connections
- Shared CPU

---

## Need Help?

- **Streamlit Docs**: https://docs.streamlit.io/
- **Community Forum**: https://discuss.streamlit.io/
- **GitHub Issues**: Report bugs on your repo

---

## Summary of Commands

```cmd
# Setup Git
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# Initialize and push to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR-USERNAME/your-repo.git
git branch -M main
git push -u origin main

# Update after changes
git add .
git commit -m "Update description"
git push origin main
```

---

## Next Steps

Now that your dashboard is deployed:

1. ✅ Share the URL with stakeholders
2. ✅ Monitor usage in Streamlit Cloud dashboard
3. ✅ Set up email alerts for high-risk customers
4. ✅ Schedule model retraining pipeline
5. ✅ Add more features based on user feedback

**Congratulations!** 🎉 You've built and deployed a complete ML pipeline!
