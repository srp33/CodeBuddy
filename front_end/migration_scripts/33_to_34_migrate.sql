ALTER TABLE courses RENAME TO courses2;

CREATE TABLE courses (
  course_id integer PRIMARY KEY AUTOINCREMENT,
  title text NOT NULL UNIQUE,
  introduction text,
  visible integer NOT NULL,
  passcode text,
  date_created timestamp NOT NULL,
  date_updated timestamp NOT NULL
);

INSERT INTO courses (course_id, title, introduction, visible, passcode, date_created, date_updated)
SELECT course_id, title, introduction, visible, passcode, date_created, date_updated
FROM courses2;

DROP TABLE courses2
