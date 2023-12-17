CREATE TABLE assignments2 (
  course_id integer NOT NULL,
  assignment_id integer PRIMARY KEY AUTOINCREMENT,
  title text NOT NULL,
  introduction text,
  visible integer NOT NULL,
  start_date timestamp,
  due_date timestamp,
  allow_late integer,
  late_percent real,
  view_answer_late integer,
  has_timer int NOT NULL,
  hour_timer int,
  minute_timer int,
  date_created timestamp NOT NULL,
  date_updated timestamp NOT NULL,
  allowed_ip_addresses text DEFAULT NULL,
  restrict_other_assignments integer NOT NULL DEFAULT 0,
  allowed_external_urls text NOT NULL DEFAULT "",
  use_virtual_assistant integer NOT NULL DEFAULT 0,
  show_run_button integer DEFAULT 1);

INSERT INTO assignments2
SELECT course_id, assignment_id, title, introduction, visible, start_date, due_date, allow_late, late_percent, view_answer_late, has_timer, hour_timer, minute_timer, date_created, date_updated, allowed_ip_addresses, restrict_other_assignments, allowed_external_urls, use_virtual_assistant, show_run_button
FROM assignments;

DROP TABLE assignments;

ALTER TABLE assignments2 RENAME TO assignments;

DROP TABLE help_requests;
