SELECT COUNT(*) AS count
FROM sqlite_master
WHERE type = "table"
  AND name = "exercise_comments"
