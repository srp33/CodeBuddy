SELECT COUNT(*) == 0 AS count
FROM pragma_table_info("courses")
WHERE name = "consent_alternative_text"
