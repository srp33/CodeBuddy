CREATE TABLE presubmissions2 (
    course_id integer NOT NULL,
    assignment_id integer NOT NULL,
    exercise_id integer NOT NULL,
    user_id text NOT NULL PRIMARY KEY,
    code text,
    date_updated datetime DEFAULT CURRENT_TIMESTAMP);

INSERT INTO presubmissions2
SELECT course_id, assignment_id, exercise_id, user_id, code, datetime()
FROM presubmissions;

DROP TABLE presubmissions;

ALTER TABLE presubmissions2 RENAME TO presubmissions
