SELECT sql NOT LIKE '%user_id text NOT NULL PRIMARY KEY%' AS count
FROM sqlite_master
WHERE type='table'
  AND name='presubmissions'