course_id, assignment_id, exercise_id, user_id, code,
CREATE TABLE IF NOT EXISTS presubmissions (
                        course_id integer NOT NULL,
                        assignment_id integer NOT NULL,
                        exercise_id integer PRIMARY KEY AUTOINCREMENT,
                        user_id text NOT NULL,
                        presubmission_id integer PRIMARY KEY AUTOINCREMENT,
                        code text,
                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE ON UPDATE CASCADE
                        FOREIGN KEY (exercise_id) REFERENCES exercises (exercise_id) ON DELETE CASCADE ON UPDATE CASCADE);
