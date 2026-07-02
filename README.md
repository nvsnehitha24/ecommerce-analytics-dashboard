# 📊 India E-commerce Sales Analytics Dashboard

End-to-end data analytics project: data generation → SQL analysis → Pandas EDA →
interactive Streamlit dashboard. Built as a portfolio project for Data Analyst
internship applications.

**[Live Dashboard →](#) | [Dataset](data/ecommerce_sales_india.csv) | [SQL Queries](sql/analysis_queries.sql)**

---

## 1. Project Overview

Analyzed **65,000 orders** (₹45.2 Cr in revenue) from a simulated Indian
e-commerce platform spanning **Jan 2022 – Dec 2023**, across 20 cities, 6
categories, and 3 customer segments. The goal: identify the levers that most
affect revenue, margin, and customer experience, and surface them in a
self-serve dashboard so stakeholders don't need to ask an analyst for every
new cut of the data.

**Why a synthetic dataset?** It was generated with realistic, documented
business rules (festive-season seasonality, city-tier demand skew,
category-specific margins, delivery-time effects on ratings — see
[`data/generate_data.py`](data/generate_data.py)), which means every insight
below can be independently verified against the generation logic and the SQL
queries. This also sidesteps licensing restrictions on redistributing scraped
marketplace data. The same pipeline works unchanged on a real Kaggle/Flipkart/
Amazon-India export — swap the CSV and the schema.

## 2. Tech Stack

| Layer | Tools |
|---|---|
| Data generation & cleaning | Python, Pandas, NumPy |
| Querying & aggregation | SQL (SQLite) |
| Exploratory analysis | Pandas, NumPy |
| Dashboard / visualization | Streamlit, Plotly |

## 3. Project Structure

```
ecommerce_analytics/
├── data/
│   ├── generate_data.py        # Synthetic data generator (documented business rules)
│   ├── ecommerce_sales_india.csv
│   └── ecommerce.db            # SQLite database used for SQL analysis
├── sql/
│   └── analysis_queries.sql    # 12 business-question SQL queries
├── notebooks/
│   └── eda_pandas.py           # Pandas EDA producing the 5 key insights
├── dashboard/
│   └── app.py                  # Streamlit interactive dashboard
├── requirements.txt
└── README.md
```

## 4. Key Insights

All figures below are pulled directly from the SQL/Pandas analysis — see
`sql/analysis_queries.sql` (query blocks 2, 3, 7, 11, 12) and
`notebooks/eda_pandas.py` to reproduce them.

1. **Festive season drives outsized revenue.** October–November (Diwali
   season) generated **22.7% of two-year revenue in just 2 of 24 months**,
   coinciding with average discounts of 22.5% vs. 7.5% in regular months —
   confirming discounting, not just organic demand, drives the spike.
2. **Electronics dominates revenue but erodes margin.** Electronics drives
   **71% of total revenue** at only a **7.0% profit margin**, while Beauty
   and Fashion contribute far less revenue (1.6% and 5.4%) but convert it at
   **30% and 26% margins** — a classic volume-vs-profitability tradeoff worth
   flagging to category management.
3. **Tier-1 cities are disproportionately valuable.** The 5 Tier-1 cities
   (25% of cities tracked) generate **43.8% of total revenue**, vs. 23.2%
   from 8 Tier-3 cities — supporting tighter logistics/inventory investment
   in fewer metro hubs.
4. **Delivery speed is a leading indicator of satisfaction.** Average rating
   falls from **4.50 (1-day delivery) to 4.06 (8-day delivery)**, a
   statistically clear downward trend (correlation −0.20) — every extra day
   of delivery time has a measurable CX cost.
5. **Repeat customers are the real revenue engine.** ~90% of customers are
   repeat buyers, and their average lifetime value (**₹27,899**) is **4.0×**
   that of one-time buyers (₹7,011) — reinforcing retention over pure
   acquisition spend.

## 5. Dashboard Features

- KPI summary: revenue, profit, margin, AOV, return rate
- Interactive filters: date range, category, city tier, customer segment
- Monthly revenue trend with festive-season annotation
- Category revenue-vs-margin comparison
- Delivery speed vs. rating trend line
- Top 10 cities by revenue
- Customer segment breakdown
- Return-rate table by category (with revenue lost to returns)

## 6. How to Run Locally

```bash
# 1. Clone and set up
git clone <your-repo-url>
cd ecommerce_analytics
pip install -r requirements.txt

# 2. (Re)generate the dataset — optional, CSV/DB are already included
python data/generate_data.py

# 3. Run the SQL analysis (prints results to console)
python -c "import sqlite3, pandas as pd; conn = sqlite3.connect('data/ecommerce.db'); [print(pd.read_sql_query(q, conn), '\n') for q in open('sql/analysis_queries.sql').read().split(';') if 'SELECT' in q.upper()]"

# 4. Run the Pandas EDA
python notebooks/eda_pandas.py

# 5. Launch the dashboard
streamlit run dashboard/app.py
```

## 7. Deploying the Dashboard (free, ~10 minutes)

1. Push this folder to a public GitHub repo.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with
   GitHub, click "New app," point it at `dashboard/app.py`.
3. Copy the live URL — put it in your resume and LinkedIn.

## 8. Possible Extensions

- Swap in a real dataset (Kaggle "Indian E-commerce" / "Superstore" /
  Flipkart product review data) — the pipeline is schema-agnostic with minor
  column-name edits.
- Add cohort retention analysis and RFM customer segmentation.
- Add a Power BI/Tableau version alongside Streamlit to show tool range.
- Add basic forecasting (e.g. Prophet or simple moving average) for next-
  quarter revenue.

---

*This is a self-initiated portfolio project built to demonstrate the
end-to-end data analytics workflow — data generation/cleaning, SQL,
Python/Pandas analysis, and dashboard development — for Data Analyst
internship applications.*
