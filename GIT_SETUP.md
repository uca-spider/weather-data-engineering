# Git Setup Instructions

Please run these commands manually to complete Sprint 0.

## Step 0: Rename Directory (if needed)

If your current directory is still `data-engineer`, rename it first:

```bash
cd /c/Portofolio
mv data-engineer weather-data-engineering
cd weather-data-engineering
```

## Step 1: Initialize Git Repository

```bash
cd /c/Portofolio/weather-data-engineering
git init
```

## Step 2: Add All Files

```bash
git add .
```

## Step 3: Create Initial Commit

**IMPORTANT**: This will commit with YOUR name (uca-spider) and email (ucaspider@gmail.com), NOT Claude.

```bash
git commit -m "Initial project setup

- Add comprehensive documentation (README, SETUP, ARCHITECTURE, COST_ESTIMATE, API_DOCS)
- Create sprint planning tracker
- Setup project structure
- Add Python requirements
- Configure environment template
- Setup .gitignore for security"
```

## Step 4: Verify Commit Author

```bash
git log --pretty=format:"%h - %an <%ae> : %s" -1
```

Expected output:
```
<hash> - uca-spider <ucaspider@gmail.com> : Initial project setup
```

## Step 5: Create GitHub Repository (Optional but Recommended)

1. Go to: https://github.com/new
2. Repository name: `weather-data-engineering`
3. Description: `End-to-end weather data engineering pipeline with Airflow, BigQuery, dbt, and Streamlit`
4. Make it **Public** (for portfolio visibility)
5. Don't initialize with README (we already have one)
6. Click "Create repository"

## Step 6: Connect to GitHub

```bash
# Add remote
git remote add origin https://github.com/uca-spider/weather-data-engineering.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

## Step 7: Verify on GitHub

- Check repository: https://github.com/uca-spider/weather-data-engineering
- Verify README displays correctly
- Check commits show your name

---

## ✅ Sprint 0 Completion Checklist

Once you've run the commands above:

- [x] Documentation files created (5 MD files)
- [x] Sprint planning tracker created
- [x] Project structure created
- [x] Python dependencies documented
- [x] Environment template created
- [x] .gitignore configured
- [ ] Git repository initialized (run commands above)
- [ ] Initial commit created (run commands above)
- [ ] GitHub repository created (optional but recommended)
- [ ] Remote repository connected (optional)

---

## 🎯 After Sprint 0 Completion

You'll be ready for **Sprint 1: Infrastructure Setup**

Next tasks:
1. Create GCP project
2. Setup BigQuery dataset
3. Create docker-compose.yml
4. Start Airflow locally

Estimated time: 4-6 hours

---

**Run the commands above, then let me know when Sprint 0 is complete!**
