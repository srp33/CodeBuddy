CREATE TABLE "presubmissions2" (
	"course_id"	integer NOT NULL,
	"assignment_id"	integer NOT NULL,
	"exercise_id"	integer NOT NULL,
	"user_id"	text NOT NULL,
	"code"	text,
	"date_updated"	datetime DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("exercise_id","user_id")
);

INSERT INTO presubmissions2
SELECT *
FROM presubmissions;

DROP TABLE presubmissions;

ALTER TABLE presubmissions2 RENAME TO presubmissions