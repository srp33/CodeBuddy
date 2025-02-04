--count should be zero if the migration changes have not been made.
SELECT COUNT(*) > 0 as count
FROM pragma_table_info('presubmissions') 
WHERE name = 'presubmission'