ALTER TABLE problems ADD COLUMN hint text;

ALTER TABLE problems ADD COLUMN show_student_submissions integer NOT NULL DEFAULT 0;