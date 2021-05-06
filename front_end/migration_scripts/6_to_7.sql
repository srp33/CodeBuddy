CREATE TABLE IF NOT EXISTS problems2 (
                        course_id integer NOT NULL,
                        assignment_id integer NOT NULL,
                        problem_id integer PRIMARY KEY AUTOINCREMENT,
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
                        show_test_code integer NOT NULL,
                        starter_code text,
                        test_code text,
                        date_created timestamp NOT NULL,
                        date_updated timestamp NOT NULL,
                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE ON UPDATE CASCADE);

INSERT INTO problems2
SELECT course_id, assignment_id, problem_id, title, visible, answer_code, answer_description, hint, max_submissions, credit,
       data_contents, back_end, expected_text_output, expected_image_output, instructions, output_type, show_answer, show_student_submissions,
       show_expected, show_test_code, starter_code, test_code, date_created, date_updated
FROM problems
