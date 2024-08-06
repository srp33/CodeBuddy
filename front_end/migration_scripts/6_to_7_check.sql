SELECT COUNT(*) AS count
FROM pragma_table_info("problems")
WHERE name = "data_files"