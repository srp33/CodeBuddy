CREATE TABLE virtual_assistant_interactions (
    course_id integer,
    assignment_id integer,
    exercise_id integer,
    user_id text,
    interaction_number integer PRIMARY KEY AUTOINCREMENT,
    question text,
    response text
)