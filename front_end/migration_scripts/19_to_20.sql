CREATE TABLE IF NOT EXISTS submission_outputs2 (
                        course_id integer NOT NULL,
                        assignment_id integer NOT NULL,
                        exercise_id integer NOT NULL,
                        user_id integer NOT NULL,
                        submission_id integer NOT NULL,
                        submission_output_id integer NOT NULL,
                        text_output text,
                        image_output text,
                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (exercise_id) REFERENCES exercises (exercise_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        PRIMARY KEY (course_id, assignment_id, exercise_id, user_id, submission_id, submission_output_id)
);

INSERT INTO submission_outputs2
    SELECT *
    FROM submission_outputs;

DROP TABLE submission_outputs;

ALTER TABLE submission_outputs2 RENAME TO submission_outputs;
