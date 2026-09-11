UPDATE assignments
SET require_security_codes = 1
WHERE require_security_codes != 0;
