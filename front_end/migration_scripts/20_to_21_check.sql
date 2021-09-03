SELECT MAX(count) = 0 as count
FROM (
  SELECT COUNT(*) as count
  FROM exercises
  GROUP BY course_id, assignment_id, title
  HAVING count > 1
)
