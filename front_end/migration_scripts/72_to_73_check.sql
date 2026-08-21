SELECT COUNT(*) AS count
FROM pragma_table_info("scores")
WHERE name = "date_updated"
