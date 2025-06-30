CREATE INDEX idx_courses_lookup
ON exercises(course_id);

CREATE INDEX idx_assignments_lookup
ON exercises(course_id, assignment_id);

CREATE INDEX idx_exercises_lookup
ON exercises(course_id, assignment_id, exercise_id);

CREATE INDEX idx_submissions_lookup
ON submissions(course_id, assignment_id, exercise_id, user_id);

CREATE INDEX idx_presubmissions_lookup
ON presubmissions(course_id, assignment_id, exercise_id, user_id);

CREATE INDEX idx_tests_lookup
ON tests(course_id, assignment_id, exercise_id);

CREATE INDEX idx_submissions_user
ON submissions(user_id);

CREATE INDEX idx_outputs_joins
ON test_outputs(test_id, submission_id);

CREATE INDEX idx_users_userid
ON users(user_id);

UPDATE exercises
SET max_submissions = 0
WHERE back_end = "multiple_choice"
