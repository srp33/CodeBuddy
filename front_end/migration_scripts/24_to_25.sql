DROP TABLE IF EXISTS user_assignment_start;

CREATE TABLE submissions2 (
  course_id integer NOT NULL,
  assignment_id integer NOT NULL,
  exercise_id integer NOT NULL,
  user_id text NOT NULL,
  submission_id integer NOT NULL,
  code text NOT NULL,
  passed integer NOT NULL,
  date timestamp NOT NULL,
  partner_id text DEFAULT NULL,
  FOREIGN KEY (course_id) REFERENCES "courses" (course_id) ON DELETE CASCADE,
  FOREIGN KEY (assignment_id) REFERENCES "assignments" (assignment_id) ON DELETE  CASCADE,
  FOREIGN KEY (exercise_id) REFERENCES "exercises" (exercise_id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES "users" (user_id) ON DELETE CASCADE,
  PRIMARY KEY (submission_id AUTOINCREMENT)
);

INSERT INTO submissions2 (course_id, assignment_id, exercise_id, user_id, code, passed, date, partner_id)
SELECT course_id, assignment_id, exercise_id, user_id, code, passed, date, partner_id
FROM submissions;

DROP TABLE IF EXISTS submissions;

ALTER TABLE submissions2 RENAME TO submissions;

CREATE TABLE test_outputs (
  test_id integer NOT NULL,
  submission_id integer NOT NULL,
  txt_output text,
  jpg_output text,
  FOREIGN KEY (test_id) REFERENCES tests (test_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (submission_id) REFERENCES submissions (submission_id) ON DELETE CASCADE ON UPDATE CASCADE
);

ALTER TABLE tests RENAME COLUMN test_instructions TO instructions;
ALTER TABLE tests RENAME COLUMN code TO after_code;
ALTER TABLE tests RENAME COLUMN text_output TO txt_output;
ALTER TABLE tests RENAME COLUMN image_output TO jpg_output;
ALTER TABLE tests ADD COLUMN title text NOT NULL DEFAULT '';
ALTER TABLE tests ADD COLUMN before_code integer NOT NULL DEFAULT '';
ALTER TABLE tests ADD COLUMN can_see_test_code integer NOT NULL DEFAULT 1;
ALTER TABLE tests ADD COLUMN can_see_expected_output integer NOT NULL DEFAULT 1;
ALTER TABLE tests ADD COLUMN can_see_code_output integer NOT NULL DEFAULT 1;

UPDATE tests
SET can_see_test_code = 1, can_see_expected_output = 1, can_see_code_output = 1
WHERE instructions = '';

UPDATE tests
SET can_see_test_code = 0, can_see_expected_output = 0, can_see_code_output = 1
WHERE instructions != '';

INSERT INTO tests (course_id, assignment_id, exercise_id, title, instructions, before_code, after_code, txt_output, jpg_output, can_see_test_code, can_see_expected_output, can_see_code_output)
SELECT course_id, assignment_id, exercise_id, 'Main output', '', '', '', expected_text_output, expected_image_output, 1, show_expected, 1
FROM exercises
WHERE (expected_text_output != '' AND expected_text_output != 'sh: 0: getcwd() failed: No such file or directory') OR expected_image_output != '';

DROP TABLE IF EXISTS submission_outputs;

CREATE TABLE exercises2 (
  course_id integer NOT NULL,
  assignment_id integer NOT NULL,
  exercise_id integer PRIMARY KEY AUTOINCREMENT,
  title text NOT NULL,
  visible integer NOT NULL,
  solution_code text NOT NULL,
  solution_description text,
  hint text,
  max_submissions integer NOT NULL,
  credit text,
  data_files text,
  back_end text NOT NULL,
  instructions text NOT NULL,
  output_type text NOT NULL,
  show_instructor_solution integer NOT NULL,
  show_peer_solution integer NOT NULL,
  starter_code text,
  date_created timestamp NOT NULL,
  date_updated timestamp NOT NULL,
  enable_pair_programming integer NOT NULL DEFAULT 0,
  verification_code text DEFAULT "",
  allow_any_response integer NOT NULL DEFAULT 0,
  FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE ON UPDATE CASCADE);

INSERT INTO exercises2
SELECT course_id,
       assignment_id,
       exercise_id,
       title,
       visible,
       answer_code,
       answer_description,
       hint,
       max_submissions,
       credit,
       data_files,
       back_end,
       instructions,
       output_type,
       show_answer,
       show_student_submissions,
       starter_code,
       date_created,
       date_updated,
       enable_pair_programming,
       check_code,
       allow_any_response
FROM exercises;

DROP TABLE IF EXISTS exercises;

ALTER TABLE exercises2 RENAME TO exercises;

DELETE
FROM presubmissions
