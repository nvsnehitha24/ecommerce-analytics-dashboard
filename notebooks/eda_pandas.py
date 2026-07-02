"""
Exploratory Data Analysis — India E-commerce Sales
Pandas/NumPy analysis producing the 5 key business insights used in the
dashboard and README. Run: python notebooks/eda_pandas.py
"""
import pandas as pd
import numpy as np

pd.set_option("display.float_format", lambda x: f"{x:,.2f}")

df = pd.read_csv("data/ecommerce_sales_india.csv", parse_dates=["Order_Date"])

print("=" * 70)
print("DATA OVERVIEW")
print("=" * 70)
print(f"Rows: {len(df):,} | Columns: {df.shape[1]} | "
      f"Date range: {df.Order_Date.min().date()} to {df.Order_Date.max().date()}")
print(f"Missing values: {df.isna().sum().sum()}")
print(f"Duplicate Order_IDs: {df.Order_ID.duplicated().sum()}")

# ------------------------------------------------------------------
# Insight 1: Festive season lift
# ------------------------------------------------------------------
df["Month_Num"] = df.Order_Date.dt.month
festive = df[df.Month_Num.isin([10, 11])]
regular = df[~df.Month_Num.isin([10, 11])]
festive_share = festive.Sales_Amount.sum() / df.Sales_Amount.sum() * 100
print("\n" + "=" * 70)
print("INSIGHT 1 — Festive Season (Oct–Nov) Revenue Lift")
print("=" * 70)
print(f"Festive months revenue share: {festive_share:.1f}% (from only 2 of 12 months)")
print(f"Avg discount — Festive: {festive.Discount_Percent.mean():.1f}% "
      f"vs Regular: {regular.Discount_Percent.mean():.1f}%")

# ------------------------------------------------------------------
# Insight 2: Revenue-heavy but low-margin category
# ------------------------------------------------------------------
cat_summary = df.groupby("Category").agg(
    Revenue=("Sales_Amount", "sum"), Profit=("Profit", "sum"), Orders=("Order_ID", "count"))
cat_summary["Margin_Pct"] = (cat_summary.Profit / cat_summary.Revenue * 100).round(2)
cat_summary["Revenue_Share_Pct"] = (cat_summary.Revenue / cat_summary.Revenue.sum() * 100).round(2)
cat_summary = cat_summary.sort_values("Revenue", ascending=False)
print("\n" + "=" * 70)
print("INSIGHT 2 — Category Revenue vs Margin")
print("=" * 70)
print(cat_summary[["Revenue", "Revenue_Share_Pct", "Margin_Pct"]])

# ------------------------------------------------------------------
# Insight 3: Tier-1 city concentration
# ------------------------------------------------------------------
tier_summary = df.groupby("City_Tier").Sales_Amount.sum()
tier_share = (tier_summary / tier_summary.sum() * 100).round(2)
print("\n" + "=" * 70)
print("INSIGHT 3 — City Tier Revenue Concentration")
print("=" * 70)
print(tier_share)

# ------------------------------------------------------------------
# Insight 4: Delivery speed vs rating correlation
# ------------------------------------------------------------------
corr = df.Delivery_Days.corr(df.Rating)
delivery_rating = df.groupby("Delivery_Days").Rating.mean()
print("\n" + "=" * 70)
print("INSIGHT 4 — Delivery Speed vs Customer Rating")
print("=" * 70)
print(f"Correlation (Delivery_Days vs Rating): {corr:.2f}")
print(f"Rating at 1-day delivery: {delivery_rating.loc[1]:.2f} | "
      f"Rating at 8-day delivery: {delivery_rating.loc[8]:.2f}")

# ------------------------------------------------------------------
# Insight 5: Repeat customers drive disproportionate value
# ------------------------------------------------------------------
cust = df.groupby("Customer_ID").agg(Orders=("Order_ID", "count"),
                                      Spend=("Sales_Amount", "sum"))
cust["Type"] = np.where(cust.Orders == 1, "One-time", "Repeat")
ltv_summary = cust.groupby("Type").agg(Customers=("Spend", "count"), Avg_LTV=("Spend", "mean"))
repeat_pct = (cust.Type == "Repeat").mean() * 100
print("\n" + "=" * 70)
print("INSIGHT 5 — Repeat Customer Value")
print("=" * 70)
print(ltv_summary)
print(f"\n{repeat_pct:.1f}% of customers are repeat buyers")
print(f"Repeat customer LTV is {ltv_summary.loc['Repeat','Avg_LTV'] / ltv_summary.loc['One-time','Avg_LTV']:.1f}x "
      f"that of one-time buyers")

print("\n" + "=" * 70)
print("Done. See README.md for the full written summary of these insights.")
