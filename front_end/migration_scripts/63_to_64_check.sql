--count should be zero if the migration changes have not been made.
SELECT COUNT(*) > 0 AS count
FROM pragma_table_info('exercises')
WHERE name = 'max_solution_length'
