SELECT COUNT(*) AS count
FROM pragma_table_info("assignments")
WHERE name = "show_run_button"