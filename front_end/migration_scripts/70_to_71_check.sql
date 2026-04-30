SELECT COUNT(*) AS count
FROM pragma_table_info("assignments")
WHERE name = "allow_students_view_submissions"
