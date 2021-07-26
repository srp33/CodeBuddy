SELECT COUNT(*) AS count
FROM pragma_table_info("users")
WHERE name = "not_sure_how_to_check_for_dropping_a_column"
