CREATE TABLE IF NOT EXISTS tests (
                        course_id integer NOT NULL,
                        assignment_id integer NOT NULL,
                        exercise_id integer NOT NULL,
                        test_id integer NOT NULL PRIMARY KEY,
                        code text,
                        text_output text,
                        image_output text,
                        show_code integer NOT NULL DEFAULT 0,
                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE ON UPDATE CASCADE
                        FOREIGN KEY (exercise_id) REFERENCES exercises (exercise_id) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE IF NOT EXISTS submission_outputs (
                        course_id integer NOT NULL,
                        assignment_id integer NOT NULL,
                        exercise_id integer NOT NULL,
                        user_id integer NOT NULL,
                        submission_id integer NOT NULL,
                        test_id integer NOT NULL PRIMARY KEY,
                        text_output text,
                        image_output text,
                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (exercise_id) REFERENCES exercises (exercise_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (submission_id) REFERENCES submissions (submission_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (test_id) REFERENCES tests (test_id) ON DELETE CASCADE ON UPDATE CASCADE);

INSERT INTO tests (
            course_id, assignment_id, exercise_id, code, show_code)
            SELECT course_id, assignment_id, exercise_id, test_code, show_test_code
            FROM exercises
            WHERE test_code IS NOT NULL;

-- ALTER TABLE exercises DROP COLUMN test_code;
-- ALTER TABLE exercises DROP COLUMN show_test_code;
