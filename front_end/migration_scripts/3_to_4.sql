PRAGMA foreign_keys=off;

CREATE TABLE IF NOT EXISTS users2 (
                        user_id text PRIMARY KEY,
                        name text,
                        given_name text,
                        family_name text,
                        picture text,
                        locale text,
                        ace_theme text NOT NULL DEFAULT "tomorrow");

INSERT INTO users2
                       SELECT user_id, "[Unknown]", "[Unknown]", "[Unknown]", "", "", "tomorrow"
                       FROM users;

CREATE TABLE IF NOT EXISTS courses2 (
                                    course_id integer PRIMARY KEY AUTOINCREMENT,
                                    title text NOT NULL UNIQUE,
                                    introduction text,
                                    visible integer NOT NULL,
                                    passcode text,
                                    date_created timestamp NOT NULL,
                                    date_updated timestamp NOT NULL
                                  );

INSERT INTO courses2
                       SELECT course_id, title, introduction, visible, NULL, date_created, date_updated
                       FROM courses;

CREATE TABLE IF NOT EXISTS course_registration (
                        user_id text NOT NULL,
                        course_id integer NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users2 (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (course_id) REFERENCES courses2 (course_id) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE IF NOT EXISTS permissions2 (
                        user_id text NOT NULL,
                        role text NOT NULL,
                        course_id integer,
                        FOREIGN KEY (user_id) REFERENCES users2 (user_id) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE IF NOT EXISTS assignments2 (
                        course_id integer NOT NULL,
                        assignment_id integer PRIMARY KEY AUTOINCREMENT,
                        title text NOT NULL,
                        introduction text,
                        visible integer NOT NULL,
                        start_date timestamp,
                        due_date timestamp,
                        allow_late integer,
                        late_percent real,
                        view_answer_late integer,
                        has_timer int NOT NULL,
                        hour_timer int,
                        minute_timer int,
                        date_created timestamp NOT NULL,
                        date_updated timestamp NOT NULL,
                        FOREIGN KEY (course_id) REFERENCES courses2 (course_id) ON DELETE CASCADE ON UPDATE CASCADE);

INSERT INTO assignments2
                       SELECT course_id, assignment_id, title, introduction, visible, start_date, due_date, allow_late, late_percent,
                       view_answer_late, has_timer, hour_timer, minute_timer, date_created, date_updated
                       FROM assignments;

CREATE TABLE IF NOT EXISTS problems2 (
                        course_id integer NOT NULL,
                        assignment_id integer NOT NULL,
                        problem_id integer PRIMARY KEY AUTOINCREMENT,
                        title text NOT NULL,
                        visible integer NOT NULL,
                        answer_code text NOT NULL,
                        answer_description text,
                        max_submissions integer NOT NULL,
                        credit text,
                        data_url text,
                        data_file_name text,
                        data_contents text,
                        back_end text NOT NULL,
                        expected_text_output text NOT NULL,
                        expected_image_output text NOT NULL,
                        instructions text NOT NULL,
                        output_type text NOT NULL,
                        show_answer integer NOT NULL,
                        show_expected integer NOT NULL,
                        show_test_code integer NOT NULL,
                        test_code text,
                        date_created timestamp NOT NULL,
                        date_updated timestamp NOT NULL,
                        FOREIGN KEY (course_id) REFERENCES courses2 (course_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (assignment_id) REFERENCES assignments2 (assignment_id) ON DELETE CASCADE ON UPDATE CASCADE);

INSERT INTO permissions2
                       SELECT user_id, role, course_id
                       FROM permissions;

INSERT INTO problems2
                       SELECT course_id, assignment_id, problem_id, title, visible, answer_code, answer_description, max_submissions, credit,
                       data_url, data_file_name, data_contents, back_end, expected_text_output, expected_image_output, instructions, output_type,
                       show_answer, show_expected, show_test_code, test_code, date_created, date_updated
                       FROM problems;

CREATE TABLE IF NOT EXISTS submissions2 (
                                        course_id integer NOT NULL,
                                        assignment_id integer NOT NULL,
                                        problem_id integer NOT NULL,
                                        user_id text NOT NULL,
                                        submission_id integer NOT NULL,
                                        code text NOT NULL,
                                        text_output text NOT NULL,
                                        image_output text NOT NULL,
                                        passed integer NOT NULL,
                                        date timestamp NOT NULL,
                                        FOREIGN KEY (course_id) REFERENCES courses2 (course_id) ON DELETE CASCADE,
                                        FOREIGN KEY (assignment_id) REFERENCES assignments2 (assignment_id) ON DELETE  CASCADE,
                                        FOREIGN KEY (problem_id) REFERENCES problems2 (problem_id) ON DELETE CASCADE,
                                        FOREIGN KEY (user_id) REFERENCES users2 (user_id) ON DELETE CASCADE,
                                        PRIMARY KEY (course_id, assignment_id, problem_id, user_id, submission_id)
                                      );

INSERT INTO submissions2
                       SELECT *
                       FROM submissions;

DROP TABLE IF EXISTS permissions;

DROP TABLE IF EXISTS submissions;

DROP TABLE IF EXISTS users;

DROP TABLE IF EXISTS problems;

DROP TABLE IF EXISTS assignments;

DROP TABLE IF EXISTS courses;

ALTER TABLE users2 RENAME TO users;

ALTER TABLE permissions2 RENAME TO permissions;

ALTER TABLE problems2 RENAME TO problems;

ALTER TABLE assignments2 RENAME TO assignments;

ALTER TABLE courses2 RENAME TO courses;

ALTER TABLE submissions2 RENAME TO submissions;

DELETE FROM scores;

INSERT INTO scores (course_id, assignment_id, problem_id, user_id, score)
SELECT course_id,
       assignment_id,
       problem_id,
       user_id,
       MAX(passed) * 100.0 AS score
FROM submissions
GROUP BY course_id, assignment_id, problem_id, user_id;

INSERT INTO course_registration (user_id, course_id)
SELECT DISTINCT user_id, course_id
FROM submissions;

PRAGMA foreign_keys=on;
