--count should be zero if the migration changes have not been made.
SELECT COUNT(*) AS count
FROM pragma_table_info("assignments")
WHERE name = "require_security_codes"
