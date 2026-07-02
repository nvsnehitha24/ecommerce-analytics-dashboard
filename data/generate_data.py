"""
Generates a realistic synthetic Indian E-commerce Sales dataset.
Mimics real-world patterns: festive season spikes, city-tier distribution,
category-wise margins, payment mode trends, and delivery/rating correlation.

Why synthetic: gives a clean, well-documented ground truth so every insight
in the dashboard can be verified, and avoids licensing issues with scraped
Kaggle data. The generation logic itself (seasonality, segment behavior,
margin structure) is the analytical value here.
"""
import numpy as np
import pandas as pd
from datetime import datetime

np.random.seed(42)

N_ORDERS = 65000
START_DATE = datetime(2022, 1, 1)
END_DATE = datetime(2023, 12, 31)

# ---- Reference data --------------------------------------------------
categories = {
    "Electronics": {"sub": ["Mobiles", "Laptops", "Headphones", "Smartwatch", "Cameras"],
                     "price_range": (999, 85000), "margin": (0.04, 0.10)},
    "Fashion": {"sub": ["Men's Wear", "Women's Wear", "Footwear", "Accessories"],
                "price_range": (299, 4500), "margin": (0.18, 0.35)},
    "Home & Kitchen": {"sub": ["Cookware", "Furniture", "Decor", "Appliances"],
                       "price_range": (399, 25000), "margin": (0.12, 0.25)},
    "Grocery": {"sub": ["Staples", "Snacks", "Beverages", "Personal Care"],
                "price_range": (49, 1200), "margin": (0.05, 0.12)},
    "Beauty": {"sub": ["Skincare", "Makeup", "Haircare", "Fragrance"],
               "price_range": (149, 3500), "margin": (0.20, 0.40)},
    "Sports": {"sub": ["Fitness Equipment", "Outdoor Gear", "Sportswear"],
               "price_range": (299, 15000), "margin": (0.10, 0.22)},
}

cities_tier = {
    "Mumbai": 1, "Delhi": 1, "Bengaluru": 1, "Hyderabad": 1, "Chennai": 1,
    "Pune": 2, "Ahmedabad": 2, "Kolkata": 2, "Jaipur": 2, "Lucknow": 2,
    "Surat": 2, "Chandigarh": 2,
    "Indore": 3, "Bhopal": 3, "Patna": 3, "Ranchi": 3, "Nagpur": 3,
    "Coimbatore": 3, "Guwahati": 3, "Varanasi": 3,
}
state_map = {
    "Mumbai": "Maharashtra", "Pune": "Maharashtra", "Nagpur": "Maharashtra",
    "Delhi": "Delhi", "Bengaluru": "Karnataka", "Hyderabad": "Telangana",
    "Chennai": "Tamil Nadu", "Coimbatore": "Tamil Nadu",
    "Ahmedabad": "Gujarat", "Surat": "Gujarat",
    "Kolkata": "West Bengal", "Jaipur": "Rajasthan", "Lucknow": "Uttar Pradesh",
    "Varanasi": "Uttar Pradesh", "Chandigarh": "Chandigarh",
    "Indore": "Madhya Pradesh", "Bhopal": "Madhya Pradesh",
    "Patna": "Bihar", "Ranchi": "Jharkhand", "Guwahati": "Assam",
}
city_names = list(cities_tier.keys())
city_weights = np.array([3.0 if cities_tier[c] == 1 else (1.6 if cities_tier[c] == 2 else 1.0)
                          for c in city_names])
city_weights = city_weights / city_weights.sum()

segments = ["Consumer", "Corporate", "SMB"]
segment_weights = [0.62, 0.18, 0.20]

payment_modes = ["UPI", "Credit Card", "Debit Card", "Cash on Delivery", "Net Banking"]
payment_weights = [0.42, 0.18, 0.15, 0.20, 0.05]

month_multiplier = {1: 1.15, 2: 0.9, 3: 0.95, 4: 0.9, 5: 0.95, 6: 1.0,
                     7: 0.95, 8: 1.1, 9: 1.0, 10: 1.6, 11: 1.8, 12: 1.2}

date_range = pd.date_range(START_DATE, END_DATE, freq="D")
date_weights = np.array([month_multiplier[d.month] for d in date_range], dtype=float)
date_weights = date_weights / date_weights.sum()

rows = []
category_names = list(categories.keys())
cat_weights = [0.24, 0.22, 0.16, 0.20, 0.10, 0.08]

for i in range(N_ORDERS):
    order_date = np.random.choice(date_range, p=date_weights)
    order_date = pd.Timestamp(order_date)

    city = np.random.choice(city_names, p=city_weights)
    tier = cities_tier[city]
    state = state_map[city]

    category = np.random.choice(category_names, p=cat_weights)
    cat_info = categories[category]
    sub_category = np.random.choice(cat_info["sub"])

    low, high = cat_info["price_range"]
    price = float(np.round(np.exp(np.random.uniform(np.log(low), np.log(high))), 2))

    quantity = np.random.choice([1, 1, 1, 2, 2, 3], p=[0.45, 0.2, 0.15, 0.1, 0.06, 0.04])

    base_discount = np.random.uniform(0, 15)
    if order_date.month in (10, 11):
        base_discount += np.random.uniform(5, 25)
    discount_pct = float(np.round(min(base_discount, 60), 1))

    gross_sales = round(price * quantity, 2)
    sales_amount = round(gross_sales * (1 - discount_pct / 100), 2)

    margin_low, margin_high = cat_info["margin"]
    margin_pct = np.random.uniform(margin_low, margin_high)
    profit = round(sales_amount * margin_pct, 2)

    segment = np.random.choice(segments, p=segment_weights)
    payment_mode = np.random.choice(payment_modes, p=payment_weights)

    base_delivery = {1: 2, 2: 4, 3: 6}[tier]
    delivery_days = max(1, int(np.random.normal(base_delivery, 1.5)))
    if payment_mode == "Cash on Delivery":
        delivery_days += np.random.choice([0, 1])

    rating_base = 4.4 - (delivery_days - base_delivery) * 0.15
    rating = float(np.clip(np.round(np.random.normal(rating_base, 0.6), 1), 1.0, 5.0))

    returned = np.random.choice([0, 1], p=[0.93, 0.07]) if category in ("Fashion", "Electronics") else \
               np.random.choice([0, 1], p=[0.97, 0.03])

    rows.append({
        "Order_ID": f"ORD{100000+i}",
        "Order_Date": order_date.strftime("%Y-%m-%d"),
        "Customer_ID": f"CUST{np.random.randint(1, 18000):05d}",
        "City": city,
        "State": state,
        "City_Tier": f"Tier {tier}",
        "Category": category,
        "Sub_Category": sub_category,
        "Quantity": int(quantity),
        "Unit_Price": price,
        "Discount_Percent": discount_pct,
        "Sales_Amount": sales_amount,
        "Profit": profit,
        "Customer_Segment": segment,
        "Payment_Mode": payment_mode,
        "Delivery_Days": int(delivery_days),
        "Rating": rating,
        "Returned": int(returned),
    })

df = pd.DataFrame(rows)
df.sort_values("Order_Date", inplace=True)
df.reset_index(drop=True, inplace=True)

out_path = "/home/claude/ecommerce_analytics/data/ecommerce_sales_india.csv"
df.to_csv(out_path, index=False)
print(f"Generated {len(df):,} rows -> {out_path}")
print(df.head(3).to_string())
print("\nDate range:", df.Order_Date.min(), "to", df.Order_Date.max())
print("Total Sales:", round(df.Sales_Amount.sum(), 2))
print("Total Profit:", round(df.Profit.sum(), 2))
