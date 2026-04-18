# 📊 Plotly Dashboard Portfolio

Interactive dashboard portfolio built using Plotly and Dash, deployed on a self-managed server. This project demonstrates the full data lifecycle — from API ingestion and data cleaning to transformation and visualization — with a focus on business-driven insights.

---

## 🚀 Project Overview

This project is designed to showcase:
- Data extraction from APIs and external datasets (Kaggle)
- Data storage and transformation using DuckDB as a lightweight analytical database
- Data cleaning and preprocessing using Python
- Dashboard development with Plotly/Dash
- Backend logic and callback-driven interactivity
- Deployment on a Linux-based cloud server
  
The goal is to translate raw data into actionable insights through interactive visual analytics.

---

## 🛠️ Tech Stack

### Core Languages
- Python

### Data Processing & Analytics
- Pandas  
- NumPy  
- DuckDB (lightweight analytical database)

### Data Visualization
- Plotly  
- Dash  

### Frontend
- HTML  
- CSS  

### Backend & Deployment
- Gunicorn (production WSGI server)  
- Linux (Ubuntu)  
- Cloud Hosting (DigitalOcean / VPS)

### Development Tools
- Git  
- GitHub  

---

## 📂 Project Structure
project/
│
├── app.py # Main application entry point
├── requirements.txt # Dependencies
│
├── dashboards/ # Dashboard modules
│ └── sales.py
│
├── static/ # Static assets (images)
│ └── index.html
│
├── templates/ # Reserved for future templating (HTML)
│
└── README.md

---

## 🔌 Data Workflow

1. Data Ingestion
- Data sourced from Kaggle datasets and external APIs
2. Data Storage (DuckDB Layer)
- Raw datasets are loaded into a DuckDB database
- Enables fast SQL-based querying and transformations
- Acts as an embedded analytical warehouse without external database overhead
3. Data Processing
- SQL queries (DuckDB) combined with Pandas for:
   - Cleaning
   - Feature engineering
   - Aggregations
4. Visualization
- Interactive dashboards built using Plotly
- Dash callbacks enable dynamic filtering and user interaction
5. Deployment
- Application deployed on a Linux server
- Served using Gunicorn for production stability

---

## 📸 Dashboards

### Sales Dashboard
- Location: dashboards/sales.py
- Features:
   - Interactive filters
   - KPI metrics
   - Time-series and categorical analysis
   - Dynamic Plotly visualizations

![] (static/images/sales_dashboard.png)

---

## ⚙️ Installation & Setup

```bash
# Clone repository
git clone https://github.com/kcastaneda1/Building-Ploty-Dashboard-Portfolio.git
cd Building-Ploty-Dashboard-Portfolio

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py


