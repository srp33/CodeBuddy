ALTER TABLE exercises
ADD COLUMN min_solution_length INTEGER DEFAULT 1;

ALTER TABLE exercises
ADD COLUMN max_solution_length INTEGER DEFAULT 10000;
