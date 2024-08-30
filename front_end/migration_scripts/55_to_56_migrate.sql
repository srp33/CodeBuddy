CREATE TABLE "thumbs" (
	"course_id"	INTEGER,
	"assignment_id"	INTEGER,
	"exercise_id"	INTEGER,
	"user_id"	TEXT,
	"item_description"	TEXT,
	"status"	INTEGER,
	PRIMARY KEY("course_id", "assignment_id", "exercise_id", "user_id", "item_description")
)
