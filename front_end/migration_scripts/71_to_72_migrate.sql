CREATE TABLE exercise_comments (
    course_id INTEGER NOT NULL,
    assignment_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    comment TEXT NOT NULL,
    commenter_id TEXT NOT NULL,
    date_updated TIMESTAMP NOT NULL,
    PRIMARY KEY (course_id, assignment_id, exercise_id, user_id)
);

CREATE INDEX idx_exercise_comments_lookup
ON exercise_comments (course_id, assignment_id, exercise_id, user_id);
