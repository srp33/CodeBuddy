SELECT NOT dflt_value AS count
FROM pragma_table_info("users")
WHERE name = 'use_studio_mode'
