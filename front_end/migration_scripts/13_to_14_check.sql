SELECT COUNT(*) AS count
FROM pragma_table_info("presubmissions")
WHERE name = "presubmission_id"
