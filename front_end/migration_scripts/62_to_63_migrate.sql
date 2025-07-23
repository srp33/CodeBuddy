CREATE TABLE assignment_early_exceptions (
	course_id INTEGER,
	assignment_id INTEGER,
	user_id TEXT,
    PRIMARY KEY(course_id, assignment_id, user_id)
)
