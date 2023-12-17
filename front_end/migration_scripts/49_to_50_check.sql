SELECT COUNT(*) = 0 AS count
FROM pragma_table_info("assignments")
WHERE name = "enable_help_requests"
