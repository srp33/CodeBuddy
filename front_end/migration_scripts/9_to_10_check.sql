SELECT COUNT(*) AS count
FROM pragma_table_info("help_requests")
WHERE name = "more_info_needed"
