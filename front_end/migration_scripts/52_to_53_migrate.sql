CREATE TABLE "security_codes" (
	"course_id"	INTEGER,
	"assignment_id"	INTEGER,
	"security_code"	TEXT,
	"confirmation_code"	TEXT,
	"student_id"	TEXT,
	PRIMARY KEY("course_id","assignment_id","security_code","confirmation_code")
);

ALTER TABLE assignments ADD COLUMN require_security_codes INTEGER NOT NULL DEFAULT 0
