CREATE INDEX "scores_exercises" ON "scores" (
	"exercise_id"
);

CREATE INDEX "scores_users" ON "scores" (
	"user_id"
);

CREATE INDEX "submissions_exercises" ON "submissions" (
	"exercise_id"
);

CREATE INDEX "submissions_users" ON "submissions" (
	"user_id"
)