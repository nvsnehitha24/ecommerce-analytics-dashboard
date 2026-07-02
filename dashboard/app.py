"""
India E-commerce Sales — Interactive Analytics Dashboard
Run with: streamlit run dashboard/app.py
"""
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="E-commerce Sales Analytics | India", layout="wide",
                    page_icon="📊")

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ecommerce.db")

# ---------------------------------------------------------------- styling --
st.markdown("""
<style>
    .main { background-color: #FAFAF8; }
    div[data-testid="stMetric"] {
        background: #FFFFFF; border: 1px solid #E5E1D8; border-radius: 10px;
        padding: 14px 18px;
    }
    div[data-testid="stMetricLabel"] { color: #6B6459; font-weight: 500; }
    h1, h2, h3 { color: #1F2A44; }
    .insight-box {
        background: #F4F1EA; border-left: 4px solid #C15B34;
        padding: 12px 16px; border-radius: 6px; margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM orders", conn)
    conn.close()
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    df["Month"] = df["Order_Date"].dt.to_period("M").astype(str)
    return df


df = load_data()

# ---------------------------------------------------------------- sidebar --
st.sidebar.title("Filters")
date_min, date_max = df.Order_Date.min(), df.Order_Date.max()
date_range = st.sidebar.date_input("Order date range", (date_min, date_max),
                                    min_value=date_min, max_value=date_max)
categories = st.sidebar.multiselect("Category", sorted(df.Category.unique()),
                                     default=sorted(df.Category.unique()))
city_tiers = st.sidebar.multiselect("City Tier", sorted(df.City_Tier.unique()),
                                     default=sorted(df.City_Tier.unique()))
segments = st.sidebar.multiselect("Customer Segment", sorted(df.Customer_Segment.unique()),
                                   default=sorted(df.Customer_Segment.unique()))

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start, end = date_min, date_max

mask = (
    (df.Order_Date >= start) & (df.Order_Date <= end)
    & (df.Category.isin(categories))
    & (df.City_Tier.isin(city_tiers))
    & (df.Customer_Segment.isin(segments))
)
fdf = df.loc[mask]

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing **{len(fdf):,}** of {len(df):,} orders")

# ---------------------------------------------------------------- header --
st.title("📊 India E-commerce Sales Analytics")
st.caption("Synthetic dataset · 65,000 orders · Jan 2022 – Dec 2023 · "
           "20 cities across 3 tiers · 6 categories")

if fdf.empty:
    st.warning("No orders match the selected filters.")
    st.stop()

# ---------------------------------------------------------------- KPIs --
c1, c2, c3, c4, c5 = st.columns(5)
total_rev = fdf.Sales_Amount.sum()
total_profit = fdf.Profit.sum()
margin = total_profit / total_rev * 100 if total_rev else 0
aov = fdf.Sales_Amount.mean()
returns = fdf.Returned.mean() * 100

c1.metric("Total Revenue", f"₹{total_rev/1e7:,.2f} Cr")
c2.metric("Total Profit", f"₹{total_profit/1e7:,.2f} Cr")
c3.metric("Profit Margin", f"{margin:.1f}%")
c4.metric("Avg Order Value", f"₹{aov:,.0f}")
c5.metric("Return Rate", f"{returns:.1f}%")

st.markdown("---")

# ---------------------------------------------------------------- Row 1 --
col1, col2 = st.columns((2, 1))

with col1:
    st.subheader("Monthly Revenue Trend")
    monthly = fdf.groupby("Month", as_index=False)["Sales_Amount"].sum()
    fig = px.area(monthly, x="Month", y="Sales_Amount",
                   labels={"Sales_Amount": "Revenue (₹)"})
    fig.update_traces(line_color="#C15B34", fillcolor="rgba(193,91,52,0.15)")
    fig.update_layout(height=360, plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(t=10))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="insight-box">💡 <b>Festive lift:</b> Oct–Nov (Diwali season) '
                'generates a sharp, repeatable spike each year, coinciding with the '
                'deepest discounting of the year.</div>', unsafe_allow_html=True)

with col2:
    st.subheader("Revenue by City Tier")
    tier_rev = fdf.groupby("City_Tier", as_index=False)["Sales_Amount"].sum()
    fig = px.pie(tier_rev, names="City_Tier", values="Sales_Amount", hole=0.55,
                 color_discrete_sequence=["#1F2A44", "#C15B34", "#B8B2A3"])
    fig.update_layout(height=360, margin=dict(t=10))
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------- Row 2 --
col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue vs Margin by Category")
    cat = fdf.groupby("Category", as_index=False).agg(
        Revenue=("Sales_Amount", "sum"), Profit=("Profit", "sum"))
    cat["Margin_Pct"] = (cat.Profit / cat.Revenue * 100).round(2)
    cat = cat.sort_values("Revenue", ascending=True)
    fig = go.Figure()
    fig.add_bar(y=cat.Category, x=cat.Revenue, orientation="h",
                name="Revenue (₹)", marker_color="#1F2A44")
    fig.update_layout(height=380, plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(t=10), xaxis_title="Revenue (₹)")
    st.plotly_chart(fig, use_container_width=True)
    top_margin_cat = cat.sort_values("Margin_Pct", ascending=False).iloc[0]
    low_margin_cat = cat.sort_values("Margin_Pct").iloc[0]
    st.markdown(f'<div class="insight-box">💡 <b>Volume ≠ margin:</b> the highest-revenue '
                f'category often runs the thinnest margin (~{low_margin_cat.Margin_Pct:.0f}%), '
                f'while {top_margin_cat.Category} converts a smaller share of revenue into '
                f'profit at ~{top_margin_cat.Margin_Pct:.0f}% margin.</div>',
                unsafe_allow_html=True)

with col2:
    st.subheader("Delivery Speed vs Customer Rating")
    dd = fdf.groupby("Delivery_Days", as_index=False)["Rating"].mean()
    dd = dd[dd.Delivery_Days <= 10]
    fig = px.line(dd, x="Delivery_Days", y="Rating", markers=True)
    fig.update_traces(line_color="#C15B34")
    fig.update_layout(height=380, plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(t=10), yaxis_range=[3.5, 4.7])
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="insight-box">💡 <b>Delivery drives satisfaction:</b> average '
                'rating declines steadily as delivery time increases beyond 3 days — '
                'a clear lever for CX improvement.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------- Row 3 --
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Cities by Revenue")
    top_cities = fdf.groupby("City", as_index=False)["Sales_Amount"].sum() \
                     .sort_values("Sales_Amount", ascending=False).head(10)
    fig = px.bar(top_cities.sort_values("Sales_Amount"), x="Sales_Amount", y="City",
                 orientation="h", color_discrete_sequence=["#C15B34"])
    fig.update_layout(height=380, plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(t=10), xaxis_title="Revenue (₹)")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Customer Segment Mix")
    seg = fdf.groupby("Customer_Segment", as_index=False).agg(
        Revenue=("Sales_Amount", "sum"), AOV=("Sales_Amount", "mean"),
        Orders=("Order_ID", "count"))
    fig = px.bar(seg, x="Customer_Segment", y="Revenue", color="Customer_Segment",
                 color_discrete_sequence=["#1F2A44", "#C15B34", "#B8B2A3"], text_auto=".2s")
    fig.update_layout(height=380, plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(t=10), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------- Row 4 --
st.subheader("Return Rate & Revenue Lost, by Category")
ret = fdf.groupby("Category", as_index=False).agg(
    Orders=("Order_ID", "count"), Returned=("Returned", "sum"),
    Revenue_Lost=("Sales_Amount", lambda s: s[fdf.loc[s.index, "Returned"] == 1].sum()))
ret["Return_Rate_Pct"] = (ret.Returned / ret.Orders * 100).round(2)
ret = ret.sort_values("Return_Rate_Pct", ascending=False)
st.dataframe(
    ret[["Category", "Orders", "Returned", "Return_Rate_Pct", "Revenue_Lost"]]
    .rename(columns={"Return_Rate_Pct": "Return Rate (%)", "Revenue_Lost": "Revenue Lost (₹)"}),
    use_container_width=True, hide_index=True
)

st.markdown("---")
st.caption("Built with Python, Pandas, SQLite (SQL analysis) and Streamlit/Plotly. "
           "Dataset is synthetically generated to reflect realistic Indian e-commerce patterns.")
