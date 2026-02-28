-- Feature Engineering SQL Queries for Churn Prediction
-- Run these queries to create derived features and analysis views

-- ============================================
-- 1. CUSTOMER SEGMENTATION VIEW
-- ============================================
CREATE OR REPLACE VIEW customer_segments AS
SELECT 
    customer_id,
    tenure,
    monthly_charges,
    total_charges,
    contract_type,
    payment_method,
    churned,
    -- Tenure segments
    CASE 
        WHEN tenure < 12 THEN 'New (<1 year)'
        WHEN tenure BETWEEN 12 AND 36 THEN 'Regular (1-3 years)'
        WHEN tenure > 36 THEN 'Loyal (>3 years)'
    END AS tenure_segment,
    -- Revenue segments
    CASE 
        WHEN monthly_charges < 40 THEN 'Low Value'
        WHEN monthly_charges BETWEEN 40 AND 80 THEN 'Medium Value'
        WHEN monthly_charges > 80 THEN 'High Value'
    END AS revenue_segment,
    -- Lifetime value estimate
    ROUND((tenure * monthly_charges)::NUMERIC, 2) AS estimated_ltv,
    -- Average monthly spend
    ROUND((total_charges / NULLIF(tenure, 0))::NUMERIC, 2) AS avg_monthly_spend
FROM customers;

-- ============================================
-- 2. CHURN RATE BY CONTRACT TYPE
-- ============================================
SELECT 
    contract_type,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN churned THEN 1 ELSE 0 END) AS churned_customers,
    ROUND((100.0 * SUM(CASE WHEN churned THEN 1 ELSE 0 END) / COUNT(*))::NUMERIC, 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges)::NUMERIC, 2) AS avg_monthly_charges
FROM customers
GROUP BY contract_type
ORDER BY churn_rate_pct DESC;

-- ============================================
-- 3. HIGH-RISK CUSTOMER IDENTIFICATION
-- ============================================
CREATE OR REPLACE VIEW high_risk_customers AS
SELECT 
    customer_id,
    tenure,
    monthly_charges,
    contract_type,
    payment_method,
    -- Risk score (higher = more likely to churn)
    (CASE WHEN contract_type = 'Month-to-month' THEN 30 ELSE 0 END +
     CASE WHEN payment_method = 'Electronic check' THEN 20 ELSE 0 END +
     CASE WHEN tenure < 12 THEN 25 ELSE 0 END +
     CASE WHEN monthly_charges > 80 THEN 15 ELSE 0 END +
     CASE WHEN online_security = 'No' THEN 10 ELSE 0 END) AS risk_score
FROM customers
WHERE churned = FALSE
ORDER BY risk_score DESC;

-- ============================================
-- 4. COHORT ANALYSIS - CHURN BY TENURE MONTH
-- ============================================
SELECT 
    tenure AS tenure_months,
    COUNT(*) AS customers,
    SUM(CASE WHEN churned THEN 1 ELSE 0 END) AS churned,
    ROUND((100.0 * SUM(CASE WHEN churned THEN 1 ELSE 0 END) / COUNT(*))::NUMERIC, 2) AS churn_rate_pct
FROM customers
WHERE tenure <= 72
GROUP BY tenure
ORDER BY tenure;

-- ============================================
-- 5. REVENUE IMPACT ANALYSIS
-- ============================================
SELECT 
    'Total Customers' AS metric,
    COUNT(*)::TEXT AS value
FROM customers
UNION ALL
SELECT 
    'Churned Customers',
    COUNT(*)::TEXT
FROM customers WHERE churned = TRUE
UNION ALL
SELECT 
    'Churn Rate',
    ROUND((100.0 * SUM(CASE WHEN churned THEN 1 ELSE 0 END) / COUNT(*))::NUMERIC, 2)::TEXT || '%'
FROM customers
UNION ALL
SELECT 
    'Monthly Revenue Lost',
    '$' || ROUND(SUM(monthly_charges)::NUMERIC, 2)::TEXT
FROM customers WHERE churned = TRUE
UNION ALL
SELECT 
    'Annual Revenue at Risk',
    '$' || ROUND((SUM(monthly_charges) * 12)::NUMERIC, 2)::TEXT
FROM customers WHERE churned = TRUE;

-- ============================================
-- 6. FEATURE AGGREGATIONS FOR ML
-- ============================================
CREATE OR REPLACE VIEW ml_features AS
SELECT 
    customer_id,
    tenure,
    monthly_charges,
    total_charges,
    -- Encoded contract type
    CASE WHEN contract_type = 'Month-to-month' THEN 1 ELSE 0 END AS is_monthly_contract,
    CASE WHEN contract_type = 'One year' THEN 1 ELSE 0 END AS is_yearly_contract,
    CASE WHEN contract_type = 'Two year' THEN 1 ELSE 0 END AS is_two_year_contract,
    -- Encoded payment method
    CASE WHEN payment_method = 'Electronic check' THEN 1 ELSE 0 END AS payment_electronic_check,
    CASE WHEN payment_method = 'Bank transfer' THEN 1 ELSE 0 END AS payment_bank_transfer,
    CASE WHEN payment_method = 'Credit card' THEN 1 ELSE 0 END AS payment_credit_card,
    -- Service features
    CASE WHEN internet_service = 'Fiber optic' THEN 1 ELSE 0 END AS has_fiber,
    CASE WHEN online_security = 'Yes' THEN 1 ELSE 0 END AS has_online_security,
    CASE WHEN tech_support = 'Yes' THEN 1 ELSE 0 END AS has_tech_support,
    CASE WHEN streaming_tv = 'Yes' THEN 1 ELSE 0 END AS has_streaming,
    CASE WHEN paperless_billing THEN 1 ELSE 0 END AS paperless_billing,
    -- Derived features
    ROUND((total_charges / NULLIF(tenure, 0))::NUMERIC, 2) AS avg_monthly_spend,
    CASE WHEN tenure < 12 THEN 1 ELSE 0 END AS is_new_customer,
    CASE WHEN monthly_charges > 80 THEN 1 ELSE 0 END AS is_high_spender,
    -- Target variable
    CASE WHEN churned THEN 1 ELSE 0 END AS churned
FROM customers;

-- ============================================
-- 7. PAYMENT METHOD CHURN ANALYSIS
-- ============================================
SELECT 
    payment_method,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN churned THEN 1 ELSE 0 END) AS churned_customers,
    ROUND((100.0 * SUM(CASE WHEN churned THEN 1 ELSE 0 END) / COUNT(*))::NUMERIC, 2) AS churn_rate_pct,
    ROUND(AVG(tenure)::NUMERIC, 1) AS avg_tenure_months
FROM customers
GROUP BY payment_method
ORDER BY churn_rate_pct DESC;

-- ============================================
-- USEFUL QUERIES TO RUN
-- ============================================

-- Get training dataset with all features:
-- SELECT * FROM ml_features;

-- Check data quality:
-- SELECT 
--     COUNT(*) as total_rows,
--     COUNT(DISTINCT customer_id) as unique_customers,
--     SUM(CASE WHEN tenure IS NULL THEN 1 ELSE 0 END) as null_tenure,
--     SUM(CASE WHEN monthly_charges IS NULL THEN 1 ELSE 0 END) as null_charges
-- FROM customers;

-- Get high-risk customers for retention campaign:
-- SELECT * FROM high_risk_customers LIMIT 20;
