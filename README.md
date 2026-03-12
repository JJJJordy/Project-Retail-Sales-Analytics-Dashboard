# 🛒 Retail Sales Analytics Dashboard

An interactive data analytics dashboard built with Python, SQLite, and Streamlit,
analyzing 4 years of retail sales data (2014–2017) across 9,994 orders.

## 🔗 Live Demo

[Click here to view the dashboard][ldivpcd42jh2svfvg6mdum.streamlit.app](https://w7kqkmx3epxmzehonav4r6.streamlit.app/)

## 📊 Key Business Insights

- Revenue grew consistently year-over-year, with orders nearly doubling from 969 (2014) to 1,687 (2017)
- The **Central Region** has a -10.41% average profit margin — the only region operating at a loss
- **Furniture** underperforms with just 3.88% margin despite $742K in sales
- Nearly **1 in 5 orders (18.7%)** operates at a loss, largely driven by heavy discounting
- Sales spike every **September, November & December** — consistent seasonal pattern across all years

## 🛠️ Tech Stack

- **Python** — data cleaning and feature engineering (Pandas)
- **SQLite** — data storage and SQL querying
- **Streamlit** — interactive web dashboard
- **Plotly** — data visualizations

## 📁 Project Structure

- `explore.py` — initial data exploration
- `clean.py` — data cleaning and feature engineering
- `database.py` — SQLite database setup and SQL queries
- `app.py` — Streamlit dashboard application

## 🗂️ Dataset

[Superstore Sales Dataset](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final) via Kaggle

## 🚀 Run Locally

```bash
git clone https://github.com/YOUR_USERNAME/retail-dashboard.git
cd retail-dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

```

---

## 🌐 Step 5C: Update .gitignore & Push Everything

We need to **remove `*.csv` from your `.gitignore`** since Streamlit Cloud needs the CSV file to build the database. Open `.gitignore` and remove the `*.csv` line so it looks like this:
```

venv/
**pycache**/
\*.pyc
.DS_Store
superstore.db
