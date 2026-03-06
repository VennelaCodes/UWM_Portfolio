-- =============================================================================
-- Project 1: Operational Data Review & KPI Analysis Initiative
-- SQL Queries for KPI Calculation & Data Validation
-- =============================================================================

-- These queries demonstrate the SQL component of the project.
-- They would run against a SQL Server database in a production environment.

-- =============================================================================
-- 1. DATA VALIDATION QUERIES
-- =============================================================================

-- Check for missing loan amounts
SELECT record_id, submission_date, loan_type, status
FROM operational_records
WHERE loan_amount IS NULL OR loan_amount <= 0;

-- Check for invalid processing days
SELECT record_id, processing_days, status
FROM operational_records
WHERE processing_days < 0;

-- Check for dates outside reporting period
SELECT record_id, submission_date
FROM operational_records
WHERE YEAR(submission_date) != 2024;

-- Data quality score calculation
SELECT
    COUNT(*) AS total_records,
    SUM(CASE WHEN loan_amount > 0
              AND processing_days >= 0
              AND YEAR(submission_date) = 2024
         THEN 1 ELSE 0 END) AS clean_records,
    CAST(SUM(CASE WHEN loan_amount > 0
                   AND processing_days >= 0
                   AND YEAR(submission_date) = 2024
              THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 AS data_quality_pct
FROM operational_records;

-- =============================================================================
-- 2. KPI CALCULATION QUERIES
-- =============================================================================

-- Overall KPI Dashboard
SELECT
    ROUND(AVG(CAST(processing_days AS FLOAT)), 1) AS avg_processing_days,
    ROUND(SUM(CASE WHEN status = 'Closed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS closure_rate,
    ROUND(AVG(CASE WHEN client_satisfaction_score BETWEEN 1 AND 5
              THEN client_satisfaction_score END), 2) AS avg_satisfaction,
    ROUND(SUM(CASE WHEN escalation_flag = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS escalation_rate,
    ROUND(SUM(CASE WHEN status = 'Denied' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS denial_rate
FROM operational_records
WHERE processing_days >= 0;

-- KPIs by Region
SELECT
    region,
    COUNT(*) AS total_records,
    ROUND(SUM(CASE WHEN status = 'Closed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS closure_rate,
    ROUND(AVG(CAST(processing_days AS FLOAT)), 1) AS avg_processing_days,
    ROUND(SUM(CASE WHEN escalation_flag = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS escalation_rate
FROM operational_records
WHERE processing_days >= 0
GROUP BY region
ORDER BY closure_rate DESC;

-- KPIs by Team
SELECT
    team,
    COUNT(*) AS total_records,
    ROUND(SUM(CASE WHEN status = 'Closed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS closure_rate,
    ROUND(AVG(CAST(processing_days AS FLOAT)), 1) AS avg_processing_days,
    ROUND(SUM(CASE WHEN escalation_flag = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS escalation_rate
FROM operational_records
WHERE processing_days >= 0
GROUP BY team
ORDER BY team;

-- =============================================================================
-- 3. MONTHLY TREND ANALYSIS
-- =============================================================================

SELECT
    FORMAT(submission_date, 'yyyy-MM') AS month,
    COUNT(*) AS volume,
    ROUND(SUM(CASE WHEN status = 'Closed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS closure_rate,
    ROUND(AVG(CAST(processing_days AS FLOAT)), 1) AS avg_processing_days,
    ROUND(SUM(CASE WHEN escalation_flag = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS escalation_rate
FROM operational_records
WHERE processing_days >= 0
GROUP BY FORMAT(submission_date, 'yyyy-MM')
ORDER BY month;

-- =============================================================================
-- 4. PROCESS INEFFICIENCY IDENTIFICATION
-- =============================================================================

-- Records with extended processing time
SELECT record_id, team, region, loan_type, processing_days, status
FROM operational_records
WHERE processing_days > 45
ORDER BY processing_days DESC;

-- Teams with high escalation rates
SELECT
    team,
    COUNT(*) AS total,
    SUM(CASE WHEN escalation_flag = 1 THEN 1 ELSE 0 END) AS escalations,
    ROUND(SUM(CASE WHEN escalation_flag = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS escalation_rate
FROM operational_records
GROUP BY team
HAVING SUM(CASE WHEN escalation_flag = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) > 18
ORDER BY escalation_rate DESC;

-- Processor workload and performance
SELECT
    processor,
    COUNT(*) AS records_handled,
    ROUND(SUM(CASE WHEN status = 'Closed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS closure_rate,
    ROUND(AVG(CAST(processing_days AS FLOAT)), 1) AS avg_days
FROM operational_records
WHERE processing_days >= 0
GROUP BY processor
ORDER BY records_handled DESC;

-- =============================================================================
-- 5. KPI TARGET COMPARISON
-- =============================================================================

-- Compare actual vs target (using CTE for clarity)
WITH actuals AS (
    SELECT
        ROUND(AVG(CAST(processing_days AS FLOAT)), 1) AS avg_processing_days,
        ROUND(SUM(CASE WHEN status = 'Closed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS closure_rate,
        ROUND(SUM(CASE WHEN escalation_flag = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS escalation_rate,
        ROUND(SUM(CASE WHEN status = 'Denied' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS denial_rate
    FROM operational_records
    WHERE processing_days >= 0
)
SELECT
    'Average Processing Days' AS kpi,
    30 AS target,
    avg_processing_days AS actual,
    CASE WHEN avg_processing_days <= 30 THEN 'ON TRACK' ELSE 'ABOVE TARGET' END AS status
FROM actuals
UNION ALL
SELECT
    'Closure Rate', 45, closure_rate,
    CASE WHEN closure_rate >= 45 THEN 'ON TRACK' ELSE 'BELOW TARGET' END
FROM actuals
UNION ALL
SELECT
    'Escalation Rate', 10, escalation_rate,
    CASE WHEN escalation_rate <= 10 THEN 'ON TRACK' ELSE 'ABOVE TARGET' END
FROM actuals;
