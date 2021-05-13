ALTER TABLE exercises ADD COLUMN enable_pair_programming integer NOT NULL DEFAULT 0;

ALTER TABLE submissions ADD COLUMN partner_id text DEFAULT NULL;

CREATE TABLE IF NOT EXISTS presubmissions (
                                        course_id integer NOT NULL,
                                        assignment_id integer NOT NULL,
                                        exercise_id integer NOT NULL,
                                        user_id text NOT NULL,
                                        code text NOT NULL,
                                        FOREIGN KEY (course_id) REFERENCES courses2 (course_id) ON DELETE CASCADE,
                                        FOREIGN KEY (assignment_id) REFERENCES assignments2 (assignment_id) ON DELETE  CASCADE,
                                        FOREIGN KEY (problem_id) REFERENCES problems2 (problem_id) ON DELETE CASCADE,
                                        FOREIGN KEY (user_id) REFERENCES users2 (user_id) ON DELETE CASCADE,
                                        PRIMARY KEY (course_id, assignment_id, problem_id, user_id)
                                      );