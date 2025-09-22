-- Example SQL: cohort aggregation (BigQuery / Standard SQL)
WITH sessions AS (
  SELECT user_id,
         session_ts,
         group,
         charged_in_low,
         energy_kwh
  FROM `project.dataset.ab_test_sessions`
)
SELECT
  group,
  COUNT(1) AS sessions,
  SUM(CASE WHEN charged_in_low THEN 1 ELSE 0 END) / COUNT(1) AS low_share,
  AVG(energy_kwh) AS avg_kwh
FROM sessions
GROUP BY group;
