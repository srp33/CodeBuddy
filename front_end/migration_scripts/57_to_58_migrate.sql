CREATE TABLE assignment_groups (
    assignment_group_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    title TEXT
);

ALTER TABLE assignments
ADD COLUMN assignment_group_id INTEGER