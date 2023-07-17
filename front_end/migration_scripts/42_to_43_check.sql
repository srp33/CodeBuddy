SELECT COUNT(*) AS count
FROM pragma_table_info("courses")
WHERE name = "virtual_assistant_config"
