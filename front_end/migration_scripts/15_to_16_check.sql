SELECT COUNT(*) AS count
FROM pragma_table_info("tests")
WHERE name = "code"
