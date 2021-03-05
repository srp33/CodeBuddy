ALTER TABLE problems RENAME TO exercises;

ALTER TABLE exercises RENAME COLUMN problem_id TO exercise_id;

ALTER TABLE submissions RENAME COLUMN problem_id TO exercise_id;

ALTER TABLE help_requests RENAME COLUMN problem_id TO exercise_id;

ALTER TABLE scores RENAME COLUMN problem_id TO exercise_id;

DROP TABLE IF EXISTS problems;