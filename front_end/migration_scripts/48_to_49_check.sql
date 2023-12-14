SELECT COUNT(*) AS count
FROM pragma_table_info("user_assignment_starts")
WHERE name = "ended_early"
