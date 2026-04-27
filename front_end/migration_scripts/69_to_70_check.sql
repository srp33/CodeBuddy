SELECT COUNT(*) > 0 AS count
FROM sqlite_master
WHERE type = 'table'
  AND name = 'lti_resource_links';
