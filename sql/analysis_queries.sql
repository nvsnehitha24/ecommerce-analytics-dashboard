-- ============================================================
-- E-commerce Sales Analytics — SQL Analysis
-- Database: data/ecommerce.db  |  Table: orders
-- ============================================================

-- 1. Overall business snapshot
SELECT
    COUNT(*)                         AS total_orders,
    ROUND(SUM(Sales_Amount), 2)      AS total_revenue,
    ROUND(SUM(Profit), 2)            AS total_profit,
    ROUND(SUM(Profit) * 100.0 / SUM(Sales_Amount), 2) AS overall_margin_pct,
    ROUND(AVG(Sales_Amount), 2)      AS avg_order_value
FROM orders;

-- 2. Monthly revenue trend (reveals festive-season seasonality)
SELECT
    strftime('%Y-%m', Order_Date) AS month,
    ROUND(SUM(Sales_Amount), 2)   AS revenue,
    COUNT(*)                      AS orders
FROM orders
GROUP BY month
ORDER BY month;

-- 3. Revenue and margin by category (find high-volume, low-margin traps)
SELECT
    Category,
    COUNT(*)                                          AS orders,
    ROUND(SUM(Sales_Amount), 2)                        AS revenue,
    ROUND(SUM(Profit), 2)                               AS profit,
    ROUND(SUM(Profit) * 100.0 / SUM(Sales_Amount), 2)   AS margin_pct
FROM orders
GROUP BY Category
ORDER BY revenue DESC;

-- 4. City-tier contribution to revenue
SELECT
    City_Tier,
    COUNT(*)                                    AS orders,
    ROUND(SUM(Sales_Amount), 2)                 AS revenue,
    ROUND(SUM(Sales_Amount) * 100.0 /
        (SELECT SUM(Sales_Amount) FROM orders), 2) AS pct_of_total_revenue
FROM orders
GROUP BY City_Tier
ORDER BY revenue DESC;

-- 5. Top 10 cities by revenue
SELECT City, State,
       ROUND(SUM(Sales_Amount), 2) AS revenue,
       COUNT(*) AS orders
FROM orders
GROUP BY City
ORDER BY revenue DESC
LIMIT 10;

-- 6. Customer segment behavior: AOV and order frequency
SELECT
    Customer_Segment,
    COUNT(*)                                    AS orders,
    ROUND(AVG(Sales_Amount), 2)                 AS avg_order_value,
    ROUND(SUM(Sales_Amount), 2)                 AS total_revenue,
    ROUND(AVG(Discount_Percent), 2)             AS avg_discount_pct
FROM orders
GROUP BY Customer_Segment
ORDER BY total_revenue DESC;

-- 7. Payment mode adoption and its link to delivery/returns
SELECT
    Payment_Mode,
    COUNT(*)                                     AS orders,
    ROUND(AVG(Delivery_Days), 2)                 AS avg_delivery_days,
    ROUND(AVG(Rating), 2)                        AS avg_rating,
    ROUND(SUM(Returned) * 100.0 / COUNT(*), 2)   AS return_rate_pct
FROM orders
GROUP BY Payment_Mode
ORDER BY orders DESC;

-- 8. Delivery speed vs customer rating (operational insight)
SELECT
    Delivery_Days,
    COUNT(*)          AS orders,
    ROUND(AVG(Rating), 2) AS avg_rating
FROM orders
GROUP BY Delivery_Days
ORDER BY Delivery_Days;

-- 9. Return rate by category (quality/fit issue detector)
SELECT
    Category,
    COUNT(*)                                    AS orders,
    SUM(Returned)                               AS returned_orders,
    ROUND(SUM(Returned) * 100.0 / COUNT(*), 2)  AS return_rate_pct,
    ROUND(SUM(CASE WHEN Returned=1 THEN Sales_Amount ELSE 0 END), 2) AS revenue_lost_to_returns
FROM orders
GROUP BY Category
ORDER BY return_rate_pct DESC;

-- 10. Top 5 sub-categories driving profit (not just revenue)
SELECT
    Category, Sub_Category,
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND(SUM(Sales_Amount), 2) AS total_revenue,
    ROUND(SUM(Profit) * 100.0 / SUM(Sales_Amount), 2) AS margin_pct
FROM orders
GROUP BY Category, Sub_Category
ORDER BY total_profit DESC
LIMIT 5;

-- 11. Repeat customer analysis (window function)
WITH customer_orders AS (
    SELECT Customer_ID, COUNT(*) AS order_count, SUM(Sales_Amount) AS total_spent
    FROM orders
    GROUP BY Customer_ID
)
SELECT
    CASE WHEN order_count = 1 THEN 'One-time' ELSE 'Repeat' END AS customer_type,
    COUNT(*) AS num_customers,
    ROUND(AVG(total_spent), 2) AS avg_lifetime_value
FROM customer_orders
GROUP BY customer_type;

-- 12. Festive season (Oct-Nov) lift vs rest of year
SELECT
    CASE WHEN CAST(strftime('%m', Order_Date) AS INTEGER) IN (10, 11)
         THEN 'Festive (Oct-Nov)' ELSE 'Regular' END AS period,
    COUNT(*) AS orders,
    ROUND(SUM(Sales_Amount), 2) AS revenue,
    ROUND(AVG(Discount_Percent), 2) AS avg_discount_pct
FROM orders
GROUP BY period;
