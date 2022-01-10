DROP TABLE user_assignment_start;

DROP TABLE submission_outputs;

CREATE TABLE test_submissions (
  test_id integer NOT NULL,
  submission_id integer NOT NULL,
  txt_output text,
  jpg_output text,
  FOREIGN KEY (test_id) REFERENCES submissions (test_id) ON DELETE CASCADE ON UPDATE CASCADE,
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
  show_peer_solutions integer NOT NULL,
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

DROP TABLE exercises;

ALTER TABLE exercises2 RENAME TO exercises
