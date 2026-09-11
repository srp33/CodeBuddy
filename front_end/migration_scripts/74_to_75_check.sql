-- count > 0 means the migration has already been applied (LTI tables are gone / never existed).
SELECT COUNT(*) = 0 AS count
FROM sqlite_master
WHERE type = "table"
  AND name IN ("lti_resource_links", "lti_user_links", "lti_launch_state", "lti_deployments", "lti_registrations");
