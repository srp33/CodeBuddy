CREATE TABLE virtual_assistant_interactions (
    course_id integer,
    assignment_id integer,
    exercise_id integer,
    user_id text,
    question text,
    response text,
    when_interacted datetime DEFAULT CURRENT_TIMESTAMP
)