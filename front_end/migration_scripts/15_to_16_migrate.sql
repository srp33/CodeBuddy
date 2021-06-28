CREATE TABLE IF NOT EXISTS tests (
                        course_id integer NOT NULL,
                        assignment_id integer NOT NULL,
                        exercise_id integer NOT NULL,
                        test_id integer NOT NULL PRIMARY KEY,
                        code text,
                        show_code integer NOT NULL DEFAULT 0,
                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE ON UPDATE CASCADE
                        FOREIGN KEY (exercise_id) REFERENCES exercises (exercise_id) ON DELETE CASCADE ON UPDATE CASCADE);

INSERT INTO tests (
                        course_id, assignment_id, exercise_id, code, show_code)
                        SELECT course_id, assignment_id, exercise_id, test_code, show_test_code
                        FROM exercises
                        WHERE test_code IS NOT NULL;

-- ALTER TABLE exercises DROP COLUMN test_code;
-- ALTER TABLE exercises DROP COLUMN show_test_code;

ALTER TABLE submissions ADD COLUMN tests_dict text;
ALTER TABLE exercises ADD COLUMN tests_dict text;
