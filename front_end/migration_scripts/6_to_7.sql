INSERT INTO exercises
            SELECT course_id, assignment_id, problem_id, title, visible, answer_code, answer_description, hint, max_submissions, credit,
            data_url, data_file_name, data_contents, back_end, expected_text_output, expected_image_output, instructions, output_type,
            show_answer, show_student_submissions, show_expected, show_test_code, starter_code, test_code, date_created, date_updated
            FROM problems;

ALTER TABLE submissions RENAME COLUMN problem_id TO exercise_id;

ALTER TABLE help_requests RENAME COLUMN problem_id TO exercise_id;

ALTER TABLE scores RENAME COLUMN problem_id TO exercise_id;

DROP TABLE IF EXISTS problems;