CREATE TABLE exercises2 (
	course_id integer NOT NULL,
	assignment_id integer NOT NULL,
	exercise_id integer,
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
	what_students_see_after_success integer NOT NULL,
	starter_code text,
	date_created timestamp NOT NULL,
	date_updated timestamp NOT NULL,
	enable_pair_programming integer NOT NULL DEFAULT 0,
	verification_code text,
	allow_any_response integer NOT NULL DEFAULT 0,
	FOREIGN KEY(assignment_id) REFERENCES assignments(assignment_id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(course_id) REFERENCES courses(course_id) ON DELETE CASCADE ON UPDATE CASCADE,
	PRIMARY KEY(exercise_id AUTOINCREMENT)
);

INSERT INTO exercises2
SELECT course_id,
       assignment_id,
       exercise_id,
       title,
       visible,
       solution_code,
       solution_description,
       hint,
       max_submissions,
       credit,
       data_files,
       back_end,
       instructions,
       output_type,
       CASE
         WHEN show_instructor_solution = 0 AND show_peer_solution = 0 THEN 0
         WHEN show_instructor_solution = 1 AND show_peer_solution = 0 THEN 1
         WHEN show_instructor_solution = 0 AND show_peer_solution = 1 THEN 2
         WHEN show_instructor_solution = 1 AND show_peer_solution = 1 THEN 3
         ELSE 0 END
       AS what_students_see_after_success,
       starter_code,
       date_created,
       date_updated,
       enable_pair_programming,
       verification_code,
       allow_any_response
FROM exercises;

DROP TABLE exercises;

ALTER TABLE exercises2 RENAME TO exercises;
