# 📊 Plotly Dashboard Portfolio

Interactive dashboard portfolio built using Plotly and Dash, deployed on a self-managed server. This project demonstrates the full data lifecycle — from API ingestion and data cleaning to transformation and visualization — with a focus on business-driven insights.

---

## 🚀 Project Overview

This project is designed to showcase:

- Data extraction via APIs
- Data cleaning and preprocessing
- Dashboard development using Plotly/Dash
- Backend logic and callback handling
- Deployment in a Linux server environment

The emphasis is on understanding data in context and translating it into actionable insights.

---

## 🛠️ Tech Stack

- Python
- Plotly / Dash
- Pandas / NumPy
- HTML / CSS
- Git & GitHub
- Linux (Ubuntu)
- Cloud Hosting (DigitalOcean)

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
├── static/ # Static assets (HTML, CSS, images)
│ └── index.html
│
├── templates/ # Reserved for future templating (Flask/Jinja)
│
└── README.md

---

## 🔌 Data Workflow

1. **Data Ingestion**
   - Retrieve data from APIs

2. **Data Processing**
   - Clean and transform datasets using Pandas

3. **Visualization**
   - Build interactive dashboards with Plotly

4. **Deployment**
   - Hosted on a cloud-based Linux server

---

## 📸 Dashboards

### Sales Dashboard
- Located in: `dashboards/sales.py`
- Demonstrates filtering, aggregation, and interactive visualizations

_(Add screenshots here later — highly recommended)_

---

## ⚙️ Installation & Setup

```bash
# Clone repository
git clone https://github.com/yourusername/project.git
cd project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
