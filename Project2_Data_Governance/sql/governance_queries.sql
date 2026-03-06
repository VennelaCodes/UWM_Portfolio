-- =============================================================================
-- Project 2: Data Governance & Reporting Optimization Project
-- SQL Queries for data consolidation and standardized reporting
-- =============================================================================

-- =============================================================================
-- 1. MULTI-SOURCE CONSOLIDATION
-- =============================================================================

-- Consolidate weekly team performance into monthly summaries
SELECT
    FORMAT(CAST(week_ending AS DATE), 'yyyy-MM') AS month,
    team_name,
    region,
    SUM(loans_processed) AS total_loans_processed,
    SUM(loans_closed) AS total_loans_closed,
    ROUND(AVG(avg_turnaround_days), 1) AS avg_turnaround,
    SUM(escalations) AS total_escalations,
    SUM(client_calls_handled) AS total_calls
FROM source_a_team_performance
GROUP BY FORMAT(CAST(week_ending AS DATE), 'yyyy-MM'), team_name, region;

-- Consolidate daily efficiency into monthly summaries
SELECT
    FORMAT(CAST(date AS DATE), 'yyyy-MM') AS month,
    team_id,
    SUM(applications_received) AS total_received,
    SUM(applications_reviewed) AS total_reviewed,
    ROUND(AVG(avg_review_time_hrs), 2) AS avg_review_time,
    SUM(rework_count) AS total_rework,
    SUM(system_downtime_min) AS total_downtime,
    COUNT(*) AS working_days
FROM source_c_efficiency
GROUP BY FORMAT(CAST(date AS DATE), 'yyyy-MM'), team_id;

-- Full consolidated view joining all three sources
CREATE VIEW vw_consolidated_dashboard AS
SELECT
    a.month,
    a.team_name AS team,
    a.region,
    -- Source A metrics
    a.total_loans_processed,
    a.total_loans_closed,
    a.avg_turnaround,
    a.total_escalations,
    a.total_calls,
    -- Source B metrics
    b.avg_csat_score,
    b.nps_score,
    b.responses AS survey_responses,
    b.complaint_count,
    -- Source C metrics
    c.total_received AS apps_received,
    c.total_reviewed AS apps_reviewed,
    c.avg_review_time,
    c.total_rework,
    c.total_downtime
FROM (
    SELECT FORMAT(CAST(week_ending AS DATE), 'yyyy-MM') AS month,
           team_name, region,
           SUM(loans_processed) AS total_loans_processed,
           SUM(loans_closed) AS total_loans_closed,
           ROUND(AVG(avg_turnaround_days), 1) AS avg_turnaround,
           SUM(escalations) AS total_escalations,
           SUM(client_calls_handled) AS total_calls
    FROM source_a_team_performance
    GROUP BY FORMAT(CAST(week_ending AS DATE), 'yyyy-MM'), team_name, region
) a
LEFT JOIN source_b_satisfaction b
    ON a.month = b.survey_month AND a.team_name = b.Team
LEFT JOIN (
    SELECT FORMAT(CAST(date AS DATE), 'yyyy-MM') AS month,
           team_id,
           SUM(applications_received) AS total_received,
           SUM(applications_reviewed) AS total_reviewed,
           ROUND(AVG(avg_review_time_hrs), 2) AS avg_review_time,
           SUM(rework_count) AS total_rework,
           SUM(system_downtime_min) AS total_downtime
    FROM source_c_efficiency
    GROUP BY FORMAT(CAST(date AS DATE), 'yyyy-MM'), team_id
) c ON a.month = c.month AND a.team_name = c.team_id;

-- =============================================================================
-- 2. NEW PERFORMANCE METRICS
-- =============================================================================

-- Operational Efficiency Index calculation
SELECT
    month, team,
    ROUND(
        (CAST(total_loans_closed AS FLOAT) / NULLIF(total_loans_processed, 0) * 100 * 0.4)
        + (GREATEST(0, 100 - (avg_turnaround - 20) * 2) * 0.4)
        - (LEAST(total_rework * 2, 30) * 0.6)
        + ((100 - LEAST(total_escalations, 50) * 2) * 0.4)
    , 1) AS operational_efficiency_index
FROM vw_consolidated_dashboard;

-- Capacity Utilization by team
SELECT
    month, team,
    apps_received, apps_reviewed,
    ROUND(CAST(apps_reviewed AS FLOAT) / NULLIF(apps_received, 0) * 100, 1) AS capacity_utilization_pct
FROM vw_consolidated_dashboard
ORDER BY month, team;

-- =============================================================================
-- 3. STANDARDIZED DASHBOARD QUERIES
-- =============================================================================

-- Monthly performance dashboard
SELECT
    month,
    team,
    region,
    total_loans_processed,
    total_loans_closed,
    ROUND(CAST(total_loans_closed AS FLOAT) / NULLIF(total_loans_processed, 0) * 100, 1) AS closure_rate_pct,
    avg_turnaround,
    total_escalations,
    avg_csat_score,
    nps_score,
    ROUND(CAST(apps_reviewed AS FLOAT) / NULLIF(apps_received, 0) * 100, 1) AS capacity_pct
FROM vw_consolidated_dashboard
ORDER BY month, team;

-- Team ranking by Operational Efficiency
SELECT
    team,
    ROUND(AVG(CAST(total_loans_closed AS FLOAT) / NULLIF(total_loans_processed, 0) * 100), 1) AS avg_closure_rate,
    ROUND(AVG(avg_turnaround), 1) AS avg_turnaround_days,
    SUM(total_escalations) AS total_escalations,
    RANK() OVER (ORDER BY AVG(CAST(total_loans_closed AS FLOAT) / NULLIF(total_loans_processed, 0) * 100) DESC) AS rank_by_closure
FROM vw_consolidated_dashboard
GROUP BY team;

-- =============================================================================
-- 4. DISCREPANCY DETECTION
-- =============================================================================

-- Volume mismatches between sources
SELECT
    month, team,
    total_loans_processed AS source_a_volume,
    apps_received AS source_c_volume,
    ROUND(CAST(total_loans_processed AS FLOAT) / NULLIF(apps_received, 0), 2) AS volume_ratio,
    CASE
        WHEN CAST(total_loans_processed AS FLOAT) / NULLIF(apps_received, 0) > 2.0 THEN 'HIGH MISMATCH'
        WHEN CAST(total_loans_processed AS FLOAT) / NULLIF(apps_received, 0) < 0.3 THEN 'LOW MISMATCH'
        ELSE 'OK'
    END AS mismatch_flag
FROM vw_consolidated_dashboard
WHERE CAST(total_loans_processed AS FLOAT) / NULLIF(apps_received, 0) NOT BETWEEN 0.3 AND 2.0;

-- Satisfaction inconsistencies
SELECT month, team, avg_csat_score, complaint_count, survey_responses,
       ROUND(CAST(complaint_count AS FLOAT) / NULLIF(survey_responses, 0) * 100, 1) AS complaint_rate
FROM vw_consolidated_dashboard
WHERE avg_csat_score > 4.0 AND complaint_count > 10;
