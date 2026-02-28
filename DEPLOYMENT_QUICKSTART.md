# Deployment Quick Reference

## 🚀 Quick Start Commands

### 1. Install Git (Windows)
Download: https://git-scm.com/download/win

### 2. Configure Git
```cmd
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

### 3. Setup Cloud Database
Sign up: https://www.elephantsql.com/
- Create "Tiny Turtle" free instance
- Save connection URL

### 4. Migrate Database
```cmd
python migrate_database.py
```
- Enter local password
- Paste cloud URL
- Wait for completion

### 5. Initialize Git Repo
```cmd
cd your-project-folder
git init
git add .
git commit -m "Initial commit"
```

### 6. Create GitHub Repo
https://github.com/new
- Name: `churn-prediction-dashboard`
- Visibility: Public
- Don't initialize with README

### 7. Push to GitHub
```cmd
git remote add origin https://github.com/YOUR-USERNAME/churn-prediction-dashboard.git
git branch -M main
git push -u origin main
```

### 8. Deploy to Streamlit Cloud
https://share.streamlit.io/
1. Sign in with GitHub
2. New app → Select your repo
3. Main file: `dashboard.py`
4. Advanced settings → Add secrets:
```toml
[database]
host = "your-host.com"
port = 5432
database = "your_db"
user = "your_user"
password = "your_password"
```
5. Deploy!

---

## 📁 Required Files Checklist

```
✅ dashboard.py (renamed from dashboard_cloud.py)
✅ churn_model.pkl
✅ scaler.pkl
✅ model_metrics.json
✅ feature_importance.csv
✅ requirements.txt
✅ .gitignore
✅ .streamlit/config.toml
```

---

## 🔑 Important URLs

- **Git Download**: https://git-scm.com/download/win
- **GitHub**: https://github.com/
- **ElephantSQL** (Free DB): https://www.elephantsql.com/
- **Supabase** (Alternative): https://supabase.com/
- **Streamlit Cloud**: https://share.streamlit.io/
- **Personal Access Token**: https://github.com/settings/tokens

---

## 🐛 Common Issues & Fixes

### "ModuleNotFoundError"
```cmd
# Check requirements.txt exists
pip install -r requirements.txt
```

### "Database connection failed"
- Verify secrets in Streamlit Cloud
- Test cloud DB connection locally first
- Check database has data

### "git push rejected"
```cmd
# Use Personal Access Token as password
# Generate at: github.com/settings/tokens
```

### "File not found: churn_model.pkl"
```cmd
git add *.pkl *.json *.csv
git commit -m "Add model files"
git push
```

---

## 📊 Free Tier Limits

**GitHub**: Unlimited public repos
**ElephantSQL**: 20 MB storage
**Streamlit Cloud**: 1 app, 1 GB RAM

---

## 🔄 Update Deployed App

```cmd
# Make changes locally
git add .
git commit -m "Update description"
git push
# App auto-updates!
```

---

## 🎯 Success Criteria

Your deployment is successful when:
- ✅ App loads at your-app.streamlit.app
- ✅ All 4 pages work (Overview, Performance, Prediction, Segments)
- ✅ Charts display data
- ✅ Predictions work
- ✅ No errors in logs

---

## 💡 Pro Tips

1. **Test locally first**: `streamlit run dashboard.py`
2. **Small commits**: Easier to debug
3. **Check logs**: Streamlit dashboard → Manage app → Logs
4. **Use secrets**: Never commit passwords
5. **Sleep apps wake**: Click link to wake from sleep

---

## 📞 Get Help

- Streamlit Docs: docs.streamlit.io
- Forum: discuss.streamlit.io
- Read full DEPLOYMENT_GUIDE.md for details
