CREATE TABLE when_content_updated (
        scope text PRIMARY KEY,
        when_updated timestamp
);

INSERT INTO when_content_updated
SELECT "user", datetime();

INSERT INTO when_content_updated
SELECT course_id, datetime()
FROM courses
