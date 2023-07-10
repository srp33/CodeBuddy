SELECT COUNT(*) AS count
FROM pragma_table_info("courses")
WHERE name = "virtual_buddy_config"
