CREATE TABLE IF NOT EXISTS help_requests (
                        course_id integer NOT NULL,
                        assignment_id integer NOT NULL,
                        problem_id integer NOT NULL,
                        user_id text NOT NULL,
                        code text NOT NULL,
                        text_output text NOT NULL,
                        image_output text NOT NULL,
                        student_comment text,
                        suggestion text,
                        approved integer NOT NULL,
                        suggester_id text,
                        approver_id text,
                        date timestamp NOT NULL,
                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON UPDATE CASCADE,
                        FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON UPDATE CASCADE,
                        FOREIGN KEY (problem_id) REFERENCES problems (problem_id) ON UPDATE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON UPDATE CASCADE,
                        PRIMARY KEY (course_id, assignment_id, problem_id, user_id));

ALTER TABLE users ADD COLUMN use_auto_complete integer NOT NULL DEFAULT 1;

ALTER TABLE problems ADD COLUMN starter_code text;

ALTER TABLE course_registration RENAME TO course_registrations;

ALTER TABLE user_assignment_start RENAME TO user_assignment_starts;