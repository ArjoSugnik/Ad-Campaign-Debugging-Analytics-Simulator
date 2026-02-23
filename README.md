# 📊 Ad Campaign Debugging & Analytics Simulator

A full-stack web application that simulates digital ad campaigns and automatically diagnoses performance issues using a rule-based diagnostic engine — built with Python (Flask), SQLite, and vanilla HTML/CSS/JavaScript.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=flat-square&logo=flask)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightblue?style=flat-square&logo=sqlite)
![JavaScript](https://img.shields.io/badge/Frontend-HTML%2FJS%2FCSS-yellow?style=flat-square&logo=javascript)
![Chart.js](https://img.shields.io/badge/Charts-Chart.js-pink?style=flat-square)

---

## 🎯 What It Does

You enter ad campaign data (budget, impressions, clicks, conversions) and the system:

- ✅ **Auto-calculates** CTR, CPC, and Conversion Rate
- 🔍 **Detects 6 types of campaign issues** automatically (Low CTR, High CPC, Tracking Failure, etc.)
- 🧠 **Maps each issue to root causes** and generates actionable recommendations
- 📈 **Visualizes performance** with interactive Chart.js dashboards
- 📄 **Exports PDF reports** per campaign
- 🌱 **Includes demo data** — 6 pre-built campaigns covering every issue type

---

## 🖥️ Screenshots

| Dashboard | Diagnostics | Analytics |
|-----------|-------------|-----------|
| Health score cards + alert panel | Issue detection with root causes | CTR, Conversion & Budget charts |

---

## 🗂️ Project Structure

```
ad-campaign-simulator/
├── backend/
│   ├── app.py              # Flask server — all API routes
│   ├── database.py         # SQLite setup and connection
│   ├── campaigns.py        # Create / Read / Delete campaigns
│   ├── diagnostics.py      # Rule-based diagnostic engine ⭐
│   ├── reports.py          # PDF report generator
│   ├── seed_data.py        # 6 example test campaigns
│   └── requirements.txt    # Python dependencies
└── frontend/
    ├── index.html          # Single-page app (5 tabs)
    ├── css/
    │   └── style.css       # Dark professional theme
    └── js/
        ├── api.js          # All fetch() calls to backend
        ├── charts.js       # Chart.js chart renderers
        └── app.js          # UI logic & tab navigation
```

---

## ⚡ Quick Start

### 1. Clone the repository

### 2. Install Python dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Start the backend server
```bash
python app.py
```
> Server runs at `http://localhost:5000`

### 4. Open the frontend
Open `frontend/index.html` in your browser.
> Tip: Use the **Live Server** extension in VS Code for best experience.

### 5. Load demo data
Click the **🌱 Load Demo Data** button in the sidebar to populate 6 example campaigns.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/campaigns` | List all campaigns |
| `POST` | `/api/campaigns` | Create a new campaign |
| `GET` | `/api/campaigns/:id` | Get one campaign |
| `DELETE` | `/api/campaigns/:id` | Delete a campaign |
| `GET` | `/api/diagnose/:id` | Run diagnostics on a campaign |
| `GET` | `/api/insights` | Health summary for all campaigns |
| `GET` | `/api/report/:id` | Download PDF report |
| `POST` | `/api/seed` | Load example campaigns |

---

## 🧠 How the Diagnostic Engine Works

The core of this project is `diagnostics.py` — a **rule-based system** that evaluates campaigns against industry-standard thresholds:

| Issue | Trigger | Severity | Health Deduction |
|-------|---------|----------|-----------------|
| Low CTR | CTR < 0.5% | 🔴 Critical | -25 pts |
| Low CTR | CTR < 1.0% | 🟡 Warning | -10 pts |
| High CPC | CPC > $10 | 🔴 Critical | -20 pts |
| High CPC | CPC > $5 | 🟡 Warning | -8 pts |
| Low Conversion Rate | Conv < 1% | 🔴 Critical | -25 pts |
| Low Conversion Rate | Conv < 2% | 🟡 Warning | -10 pts |
| Tracking Failure | Clicks > 100 & Conv = 0 | 🔴 Critical | -30 pts |
| Budget Exhausted | Remaining < 5% | 🔴 Critical | -15 pts |

**Health Score** starts at 100 and deductions are applied per issue:
- 🟢 **80–100** — Healthy
- 🟡 **50–79** — Warning
- 🔴 **0–49** — Critical

---

## 📦 Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend | Python + Flask | Simple REST API, readable syntax |
| Database | SQLite | Zero-config file-based database |
| Frontend | HTML + CSS + JS | No framework needed, beginner-friendly |
| Charts | Chart.js | Easy to use, beautiful visuals |
| PDF Export | ReportLab | Professional PDF generation in Python |

---

## 🌱 Demo Campaigns Included

| Campaign | Issue Simulated |
|----------|----------------|
| Spring Sale - Google Search | ✅ No issues (healthy baseline) |
| Brand Awareness - Display Network | 🔴 Low CTR Critical |
| Competitor Keywords - Search | 🔴 High CPC Critical |
| Black Friday - Retargeting | 🔴 Tracking Failure |
| Holiday Rush - Facebook | 🔴 Budget Exhausted |
| New Product Launch - Broken Campaign | 🔴 Multiple Critical Issues |

---

## 🔮 Planned Features

- [ ] User authentication (Flask-Login + JWT)
- [ ] Campaign comparison side-by-side view
- [ ] Time-series performance tracking (daily metrics history)
- [ ] Automated daily insights email/Slack alerts
- [ ] Google Ads / Meta Ads API integration
- [ ] Anomaly detection using ML (replace hard-coded thresholds)

---

## 💼 Why This Project? (For Recruiters)

This project demonstrates skills directly relevant to **Product Support Engineering** and **Ad Tech** roles:

- **Troubleshooting mindset** — the diagnostic engine replicates how support engineers debug ad campaign issues
- **API design & integration** — RESTful backend with clean separation of concerns
- **Data interpretation** — understanding CTR, CPC, ROAS, conversion funnels
- **Full-stack thinking** — end-to-end from database → API → UI → PDF export
- **Product knowledge** — tracking failure detection mirrors real-world pixel/tag debugging workflows used in Google Tag Manager and Meta Pixel

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🙋 Author

Built as a portfolio project for a **Product Support Engineer** role.  
Feel free to fork, star ⭐, or reach out with questions!
