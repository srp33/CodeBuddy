--count should be zero if the migration changes have not been made.
--The second condition accounts for the fact that we could be building the database from scratch.
SELECT
    (
        (SELECT COUNT(*) FROM presubmissions) = 0
        OR
        (SELECT COUNT(*) FROM submissions) = 0
    ) AS count;

