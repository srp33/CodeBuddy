CREATE TABLE IF NOT EXISTS asdf (
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

DROP TABLE asdf;
