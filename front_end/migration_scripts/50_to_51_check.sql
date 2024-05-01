SELECT COUNT(*) > 0 AS count
FROM sqlite_master
WHERE type='index'
  AND name='submissions_users'