CREATE TABLE IF NOT EXISTS tests (
                        course_id integer NOT NULL,
                        assignment_id integer NOT NULL,
                        exercise_id integer NOT NULL,
                        test_id integer NOT NULL PRIMARY KEY,
                        code text,
                        text_output text,
                        image_output text,
                        test_instructions text DEFAULT "",
                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE ON UPDATE CASCADE
                        FOREIGN KEY (exercise_id) REFERENCES exercises (exercise_id) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE IF NOT EXISTS submission_outputs (
                        course_id integer NOT NULL,
                        assignment_id integer NOT NULL,
                        exercise_id integer NOT NULL,
                        user_id integer NOT NULL,
                        submission_id integer NOT NULL,
                        submission_output_id integer NOT NULL PRIMARY KEY,
                        text_output text,
                        image_output text,
                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (exercise_id) REFERENCES exercises (exercise_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (submission_id) REFERENCES submissions (submission_id) ON DELETE CASCADE ON UPDATE CASCADE);

INSERT INTO tests (course_id, assignment_id, exercise_id, code)
            SELECT course_id, assignment_id, exercise_id, test_code
            FROM exercises
            WHERE test_code IS NOT NULL
              AND test_code != ""
              AND show_test_code = 1;

INSERT INTO tests (course_id, assignment_id, exercise_id, code, test_instructions)
            SELECT course_id, assignment_id, exercise_id, test_code, "Test Code Hidden."
            FROM exercises
            WHERE test_code IS NOT NULL
              AND test_code != ""
              AND show_test_code = 0;

DROP TABLE IF EXISTS course_registration;

DELETE FROM course_registrations WHERE user_id NOT IN (SELECT user_id FROM permissions WHERE role = 'administrator' or role = 'instructor');

DELETE FROM submissions WHERE user_id NOT IN (SELECT user_id FROM permissions WHERE role = 'administrator' or role = 'instructor');

DELETE FROM metadata WHERE version = 5;

DROP TABLE IF EXISTS problems;

DELETE FROM scores WHERE user_id NOT IN (SELECT user_id FROM permissions WHERE role = 'administrator' or role = 'instructor');

DROP TABLE IF EXISTS user_assignment_start;

DELETE FROM user_assignment_starts WHERE user_id NOT IN (SELECT user_id FROM permissions WHERE role = 'administrator' or role = 'instructor');

DELETE FROM users WHERE user_id NOT IN (SELECT user_id FROM permissions WHERE role = 'administrator' or role = 'instructor');
