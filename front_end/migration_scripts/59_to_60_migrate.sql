ALTER TABLE assignments
ADD COLUMN support_questions INTEGER DEFAULT 0;

CREATE TABLE questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    assignment_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    questioner_id INTEGER,
    question TEXT NOT NULL,
    questioner_share INTEGER DEFAULT 0,
    question_date TIMESTAMP NOT NULL,
    question_modified INTEGER DEFAULT 0,
    answerer_id INTEGER,
    answer TEXT,
    answerer_share INTEGER DEFAULT 0,
    answer_date TIMESTAMP
);

CREATE INDEX idx_questions_lookup
ON questions (course_id, assignment_id, exercise_id)
