-- Remove all rows from tables that have user information.

DELETE FROM submissions;
DELETE FROM permissions;
DELETE FROM course_registrations;
DELETE FROM help_requests;
DELETE FROM presubmissions;
DELETE FROM scores;
DELETE FROM submission_outputs;
DELETE FROM user_assignment_starts;
DELETE FROM users;

-- Add email_address field to users table.

ALTER TABLE users ADD COLUMN email_address text NOT NULL DEFAULT '';

-- Insert rows into users table with personal information for current admins.

INSERT INTO users (user_id, name, given_name, family_name, locale, ace_theme, use_auto_complete, enable_vim, email_address)
VALUES ('srp33', 'Stephen Piccolo', 'Stephen', 'Piccolo', 'en', 'tomorrow', 1, 0, 'nospam@nospam.edu');

INSERT INTO users (user_id, name, given_name, family_name, locale, ace_theme, use_auto_complete, enable_vim, email_address)
VALUES ('pgr2', 'Perry Ridge', 'Perry', 'Ridge', 'en', 'tomorrow', 1, 0, 'nospam@nospam.edu');

-- Insert rows to permissions table.

INSERT INTO permissions (user_id, role, course_id)
VALUES ('srp33', 'administrator', 0);
INSERT INTO permissions (user_id, role, course_id)
VALUES ('pgr2', 'administrator', 0);
