-- count > 0 means the migration has already been applied (only 0/1 values remain).
SELECT COUNT(*) = 0 AS count
FROM assignments
WHERE require_security_codes NOT IN (0, 1);
