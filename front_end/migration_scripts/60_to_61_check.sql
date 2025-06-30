--count should be zero if the migration changes have not been made.
SELECT COUNT(*) > 0 AS count
FROM pragma_index_info("idx_users_userid")
