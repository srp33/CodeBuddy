SELECT COUNT(*) AS count
FROM pragma_table_info("presubmissions")
WHERE name = "date_updated"
