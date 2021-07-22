SELECT COUNT(*) AS count
FROM pragma_table_info("courses")
WHERE name = "consent_text"
