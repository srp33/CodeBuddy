ALTER TABLE assignments ADD COLUMN secure_access_code TEXT DEFAULT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_assignments_secure_access_code
ON assignments(secure_access_code)
WHERE secure_access_code IS NOT NULL;

CREATE TABLE IF NOT EXISTS assignment_secure_authorizations (
    course_id integer NOT NULL,
    assignment_id integer NOT NULL,
    user_id text NOT NULL,
    authorized_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (course_id, assignment_id, user_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE
);
