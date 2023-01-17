SELECT COUNT(*) AS count
FROM pragma_table_info("courses")
WHERE name = "allow_students_download_submissions"
