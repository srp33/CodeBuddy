SELECT COUNT(*) AS count
FROM pragma_table_info("users")
WHERE name = "email_address"
