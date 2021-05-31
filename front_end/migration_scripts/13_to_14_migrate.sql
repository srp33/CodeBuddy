CREATE TABLE IF NOT EXISTS presubmissions (
                        course_id integer NOT NULL,
                        assignment_id integer NOT NULL,
                        exercise_id integer NOT NULL,
                        user_id text NOT NULL PRIMARY KEY,
                        code text,
                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE ON UPDATE CASCADE
                        FOREIGN KEY (exercise_id) REFERENCES exercises (exercise_id) ON DELETE CASCADE ON UPDATE CASCADE);
