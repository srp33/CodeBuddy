DROP TABLE course_registration;

DELETE FROM course_registrations WHERE user_id = 'jtgrooms' AND course_id = 9;
DELETE FROM course_registrations WHERE user_id = 'anp37' AND course_id = 4;
DELETE FROM course_registrations WHERE user_id = 'searleps' AND course_id = 4;
DELETE FROM course_registrations WHERE user_id = 'dmitton' AND course_id = 4;
DELETE FROM course_registrations WHERE user_id = 'nitz1bug' AND course_id = 4;
DELETE FROM course_registrations WHERE user_id = 'ebur2000' AND course_id = 4;
DELETE FROM course_registrations WHERE user_id = 'ebur2000' AND course_id = 10;
DELETE FROM course_registrations WHERE user_id = 'cgreen64' AND course_id = 9;
DELETE FROM course_registrations WHERE user_id = 'hboekweg' AND course_id = 4;

DELETE FROM permissions;

INSERT INTO permissions (user_id, role, course_id) VALUES ('srp33', 'administrator', 0);
INSERT INTO permissions (user_id, role, course_id) VALUES ('conbward', 'assistant', 12);
INSERT INTO permissions (user_id, role, course_id) VALUES ('shp2', 'instructor', 4);
INSERT INTO permissions (user_id, role, course_id) VALUES ('dmitton', 'assistant', 4);
INSERT INTO permissions (user_id, role, course_id) VALUES ('nitz1bug', 'assistant', 4);
INSERT INTO permissions (user_id, role, course_id) VALUES ('searleps', 'assistant', 4);
INSERT INTO permissions (user_id, role, course_id) VALUES ('anp37', 'assistant', 4);
INSERT INTO permissions (user_id, role, course_id) VALUES ('ebur2000', 'assistant', 4);
INSERT INTO permissions (user_id, role, course_id) VALUES ('hboekweg', 'assistant', 4);
INSERT INTO permissions (user_id, role, course_id) VALUES ('ebur2000', 'assistant', 4);
INSERT INTO permissions (user_id, role, course_id) VALUES ('jtgrooms', 'assistant', 9);
INSERT INTO permissions (user_id, role, course_id) VALUES ('cgreen64', 'assistant', 9);
INSERT INTO permissions (user_id, role, course_id) VALUES ('pgr2', 'instructor', 10);
INSERT INTO permissions (user_id, role, course_id) VALUES ('etatlow', 'instructor', 10);
INSERT INTO permissions (user_id, role, course_id) VALUES ('ebur2000', 'assistant', 10);
INSERT INTO permissions (user_id, role, course_id) VALUES ('anp37', 'assistant', 10);
INSERT INTO permissions (user_id, role, course_id) VALUES ('searleps', 'assistant', 10);
INSERT INTO permissions (user_id, role, course_id) VALUES ('nitz1bug', 'assistant', 10);
INSERT INTO permissions (user_id, role, course_id) VALUES ('pgr2', 'instructor', 11);
INSERT INTO permissions (user_id, role, course_id) VALUES ('jtgrooms', 'assistant', 12)
