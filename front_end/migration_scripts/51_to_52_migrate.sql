CREATE TABLE prerequisite_assignments (
	course_id INTEGER,
	assignment_id INTEGER,
	prerequisite_assignment_id INTEGER,
	PRIMARY KEY(course_id, assignment_id, prerequisite_assignment_id)
)
