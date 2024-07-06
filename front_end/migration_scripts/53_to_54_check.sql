SELECT COUNT(*) AS count
FROM pragma_table_info("assignments")
WHERE name = "custom_scoring"
