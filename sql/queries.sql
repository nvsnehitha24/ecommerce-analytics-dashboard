-- ============================================================
-- E-Commerce Analytics: Cohort, RFM, Growth & Churn Queries
-- Author: Snehitha
-- DB: SQLite — single table `orders`
--
-- Actual schema:
--   orders(Order_ID, Order_Date, Customer_ID, City, State, City_Tier,
--          Category, Sub_Category, Quantity, Unit_Price, Discount_Percent,
--          Sales_Amount, Profit, Customer_Segment, Payment_Mode,
--          Delivery_Days, Rating, Returned)
--
-- Notes:
--   - Sales_Amount is already net revenue per line (Unit_Price * Quantity,
--     discount applied) — no need to recompute from Quantity * Unit_Price.
--   - Returned = 1 means the order was returned; excluded from revenue
--     analyses below via WHERE Returned = 0.
--   - Recency is calculated relative to the LATEST Order_Date in the
--     dataset itself (this is historical data, not live), not today's
--     real-world date.
-- ============================================================


-- ------------------------------------------------------------
-- 1. MONTHLY COHORT RETENTION
-- ------------------------------------------------------------

WITH first_order AS (
    SELECT Customer_ID, MIN(strftime('%Y-%m', Order_Date)) AS cohort_month
    FROM orders
    WHERE Returned = 0
    GROUP BY Customer_ID
),
order_months AS (
    SELECT DISTINCT Customer_ID, strftime('%Y-%m', Order_Date) AS order_month
    FROM orders
    WHERE Returned = 0
),
cohort_activity AS (
    SELECT
        f.cohort_month,
        om.order_month,
        (CAST(strftime('%Y', om.order_month || '-01') AS INT) * 12
            + CAST(strftime('%m', om.order_month || '-01') AS INT))
        -
        (CAST(strftime('%Y', f.cohort_month || '-01') AS INT) * 12
            + CAST(strftime('%m', f.cohort_month || '-01') AS INT)) AS month_number,
        om.Customer_ID
    FROM order_months om
    JOIN first_order f ON f.Customer_ID = om.Customer_ID
),
cohort_size AS (
    SELECT cohort_month, COUNT(DISTINCT Customer_ID) AS num_customers
    FROM first_order
    GROUP BY cohort_month
)
SELECT
    ca.cohort_month,
    cs.num_customers AS cohort_size,
    ca.month_number,
    COUNT(DISTINCT ca.Customer_ID) AS active_customers,
    ROUND(100.0 * COUNT(DISTINCT ca.Customer_ID) / cs.num_customers, 1) AS retention_pct
FROM cohort_activity ca
JOIN cohort_size cs ON cs.cohort_month = ca.cohort_month
GROUP BY ca.cohort_month, ca.month_number
ORDER BY ca.cohort_month, ca.month_number;


-- ------------------------------------------------------------
-- 2. RFM SEGMENTATION
-- Recency measured against the latest date present in the data.
-- ------------------------------------------------------------

WITH max_date AS (
    SELECT MAX(Order_Date) AS ref_date FROM orders
),
customer_orders AS (
    SELECT
        Customer_ID,
        MAX(Order_Date) AS last_order_date,
        COUNT(DISTINCT Order_ID) AS frequency,
        SUM(Sales_Amount) AS monetary
    FROM orders
    WHERE Returned = 0
    GROUP BY Customer_ID
),
rfm_base AS (
    SELECT
        co.Customer_ID,
        CAST(julianday((SELECT ref_date FROM max_date)) - julianday(co.last_order_date) AS INT) AS recency_days,
        co.frequency,
        co.monetary
    FROM customer_orders co
),
rfm_scores AS (
    SELECT
        Customer_ID,
        recency_days,
        frequency,
        monetary,
        6 - NTILE(5) OVER (ORDER BY recency_days) AS r_score,
        NTILE(5) OVER (ORDER BY frequency)        AS f_score,
        NTILE(5) OVER (ORDER BY monetary)         AS m_score
    FROM rfm_base
)
SELECT
    Customer_ID,
    recency_days,
    frequency,
    monetary,
    r_score, f_score, m_score,
    (r_score + f_score + m_score) AS rfm_total,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 4 AND f_score >= 3                 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2                 THEN 'New Customers'
        WHEN r_score <= 2 AND f_score >= 4 AND m_score >= 4 THEN 'At Risk (High Value)'
        WHEN r_score <= 2 AND f_score <= 2                 THEN 'Churned / Lost'
        ELSE 'Needs Attention'
    END AS segment
FROM rfm_scores
ORDER BY rfm_total DESC;


-- ------------------------------------------------------------
-- 3. MONTH-OVER-MONTH REVENUE GROWTH
-- ------------------------------------------------------------

WITH monthly_revenue AS (
    SELECT
        strftime('%Y-%m', Order_Date) AS month,
        SUM(Sales_Amount) AS revenue
    FROM orders
    WHERE Returned = 0
    GROUP BY strftime('%Y-%m', Order_Date)
)
SELECT
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month) AS prev_month_revenue,
    ROUND(
        100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
        / NULLIF(LAG(revenue) OVER (ORDER BY month), 0), 1
    ) AS mom_growth_pct
FROM monthly_revenue
ORDER BY month;


-- ------------------------------------------------------------
-- 4. CHURN RATE BY RFM SEGMENT
-- "Churned" = no order in 90+ days relative to the latest date
-- present in the dataset.
-- ------------------------------------------------------------

WITH max_date AS (
    SELECT MAX(Order_Date) AS ref_date FROM orders
),
customer_orders AS (
    SELECT
        Customer_ID,
        MAX(Order_Date) AS last_order_date,
        COUNT(DISTINCT Order_ID) AS frequency,
        SUM(Sales_Amount) AS monetary
    FROM orders
    WHERE Returned = 0
    GROUP BY Customer_ID
),
rfm_base AS (
    SELECT
        co.Customer_ID,
        CAST(julianday((SELECT ref_date FROM max_date)) - julianday(co.last_order_date) AS INT) AS recency_days,
        co.frequency,
        co.monetary
    FROM customer_orders co
),
rfm_scores AS (
    SELECT
        Customer_ID,
        recency_days,
        6 - NTILE(5) OVER (ORDER BY recency_days) AS r_score,
        NTILE(5) OVER (ORDER BY frequency)        AS f_score,
        NTILE(5) OVER (ORDER BY monetary)         AS m_score
    FROM rfm_base
),
segmented AS (
    SELECT
        Customer_ID,
        recency_days,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score >= 4 AND f_score >= 3                 THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score <= 2                 THEN 'New Customers'
            WHEN r_score <= 2 AND f_score >= 4 AND m_score >= 4 THEN 'At Risk (High Value)'
            WHEN r_score <= 2 AND f_score <= 2                 THEN 'Churned / Lost'
            ELSE 'Needs Attention'
        END AS segment
    FROM rfm_scores
)
SELECT
    segment,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN recency_days > 90 THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(100.0 * SUM(CASE WHEN recency_days > 90 THEN 1 ELSE 0 END) / COUNT(*), 1) AS churn_rate_pct
FROM segmented
GROUP BY segment
ORDER BY churn_rate_pct DESC;


-- ------------------------------------------------------------
-- 5. PARETO CHECK: top 20% of customers by spend
-- ------------------------------------------------------------

WITH customer_spend AS (
    SELECT
        Customer_ID,
        SUM(Sales_Amount) AS total_spent
    FROM orders
    WHERE Returned = 0
    GROUP BY Customer_ID
),
ranked AS (
    SELECT
        Customer_ID,
        total_spent,
        NTILE(5) OVER (ORDER BY total_spent DESC) AS spend_quintile
    FROM customer_spend
)
SELECT
    spend_quintile,
    COUNT(*) AS num_customers,
    SUM(total_spent) AS quintile_revenue,
    ROUND(100.0 * SUM(total_spent) / (SELECT SUM(total_spent) FROM customer_spend), 1) AS pct_of_total_revenue
FROM ranked
GROUP BY spend_quintile
ORDER BY spend_quintile;


-- ------------------------------------------------------------
-- 6. BONUS: Churn rate by real Customer_Segment (Consumer vs Corporate)
-- Uses the actual Customer_Segment column already in the data —
-- a good complement to the RFM-derived segment above.
-- ------------------------------------------------------------

WITH max_date AS (
    SELECT MAX(Order_Date) AS ref_date FROM orders
),
customer_recency AS (
    SELECT
        Customer_ID,
        Customer_Segment,
        MAX(Order_Date) AS last_order_date
    FROM orders
    WHERE Returned = 0
    GROUP BY Customer_ID, Customer_Segment
)
SELECT
    Customer_Segment,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN julianday((SELECT ref_date FROM max_date)) - julianday(last_order_date) > 90 THEN 1 ELSE 0 END) AS churned,
    ROUND(100.0 * SUM(CASE WHEN julianday((SELECT ref_date FROM max_date)) - julianday(last_order_date) > 90 THEN 1 ELSE 0 END) / COUNT(*), 1) AS churn_rate_pct
FROM customer_recency
GROUP BY Customer_Segment
ORDER BY churn_rate_pct DESC;
