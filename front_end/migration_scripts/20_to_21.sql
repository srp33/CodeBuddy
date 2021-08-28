-- I included this line because in some of the migration runs I was seeing errors that 'show_test_code' (an obselete column, would be useful to track down each instance and remove it from the code entirely given the time)
-- was having non integers assigned to it. I didn't have the time to fully track down those errors or why an empty string would be assigned to show_test_code in the first place, so I'm leaving this here as is.

-- All this is doing is changing the type of show_test_code to text
CREATE TABLE IF NOT EXISTS exercises2 (
                        course_id integer NOT NULL,
                        assignment_id integer NOT NULL,
                        exercise_id integer PRIMARY KEY AUTOINCREMENT,
                        title text NOT NULL,
                        visible integer NOT NULL,
                        answer_code text NOT NULL,
                        answer_description text,
                        hint text,
                        max_submissions integer NOT NULL,
                        credit text,
                        data_files text,
                        back_end text NOT NULL,
                        expected_text_output text NOT NULL,
                        expected_image_output text NOT NULL,
                        instructions text NOT NULL,
                        output_type text NOT NULL,
                        show_answer integer NOT NULL,
                        show_student_submissions integer NOT NULL,
                        show_expected integer NOT NULL,
                        show_test_code text,
                        starter_code text,
                        test_code text,
                        date_created timestamp NOT NULL,
                        date_updated timestamp NOT NULL, enable_pair_programming integer NOT NULL DEFAULT 0, check_code text DEFAULT "",
                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE ON UPDATE CASCADE);

INSERT INTO exercises2
  SELECT *
  FROM exercises;

DROP TABLE exercises;

ALTER TABLE exercises2 RENAME TO exercises;
