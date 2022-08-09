SELECT COUNT(*) = 0 AS count
FROM pragma_table_info("exercises")
WHERE name = 'show_instructor_solution'
