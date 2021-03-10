# Creates tables from version 5. Any changes to this schema
# must be done via a migration script.
def database_tables():
    sql_commands = []

    sql_commands.append('''CREATE TABLE IF NOT EXISTS metadata (version integer NOT NULL);''')
    sql_commands.append('''INSERT INTO metadata (version) VALUES (5);''')

    sql_commands.append('''CREATE TABLE IF NOT EXISTS users (
                             user_id text PRIMARY KEY,
                             name text,
                             given_name text,
                             family_name text,
                             picture text,
                             locale text,
                             ace_theme text NOT NULL DEFAULT "tomorrow"
                        );''')

    sql_commands.append('''CREATE TABLE IF NOT EXISTS permissions (
                             user_id text NOT NULL,
                             role text NOT NULL,
                             course_id integer,
                           FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE
                        );''')

    sql_commands.append('''CREATE TABLE IF NOT EXISTS course_registration (
                             user_id text NOT NULL,
                             course_id integer NOT NULL,
                           FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                           FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE
                        );''')

    sql_commands.append('''CREATE TABLE IF NOT EXISTS courses (
                             course_id integer PRIMARY KEY AUTOINCREMENT,
                             title text NOT NULL UNIQUE,
                             introduction text,
                             visible integer NOT NULL,
                             passcode text,
                             date_created timestamp NOT NULL,
                             date_updated timestamp NOT NULL
                        );''')

    sql_commands.append('''CREATE TABLE IF NOT EXISTS assignments (
                             course_id integer NOT NULL,
                             assignment_id integer PRIMARY KEY AUTOINCREMENT,
                             title text NOT NULL,
                             introduction text,
                             visible integer NOT NULL,
                             start_date timestamp,
                             due_date timestamp,
                             allow_late integer,
                             late_percent real,
                             view_answer_late integer,
                             has_timer int NOT NULL,
                             hour_timer int,
                             minute_timer int,
                             date_created timestamp NOT NULL,
                             date_updated timestamp NOT NULL,
                           FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE
                        );''')

    sql_commands.append('''CREATE TABLE IF NOT EXISTS problems (
                             course_id integer NOT NULL,
                             assignment_id integer NOT NULL,
                             problem_id integer PRIMARY KEY AUTOINCREMENT,
                             title text NOT NULL,
                             visible integer NOT NULL,
                             answer_code text NOT NULL,
                             answer_description text,
                             hint text,
                             max_submissions integer NOT NULL,
                             credit text,
                             data_url text,
                             data_file_name text,
                             data_contents text,
                             back_end text NOT NULL,
                             expected_text_output text NOT NULL,
                             expected_image_output text NOT NULL,
                             instructions text NOT NULL,
                             output_type text NOT NULL,
                             show_answer integer NOT NULL,
                             show_student_submissions integer NOT NULL,
                             show_expected integer NOT NULL,
                             show_test_code integer NOT NULL,
                             test_code text,
                             date_created timestamp NOT NULL,
                             date_updated timestamp NOT NULL,
                             FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE,
                             FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE ON UPDATE CASCADE
                        );''')

    sql_commands.append('''CREATE TABLE IF NOT EXISTS submissions (
                             course_id integer NOT NULL,
                             assignment_id integer NOT NULL,
                             problem_id integer NOT NULL,
                             user_id text NOT NULL,
                             submission_id integer NOT NULL,
                             code text NOT NULL,
                             text_output text NOT NULL,
                             image_output text NOT NULL,
                             passed integer NOT NULL,
                             date timestamp NOT NULL,
                           FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE,
                           FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE ON UPDATE CASCADE,
                           FOREIGN KEY (problem_id) REFERENCES problems (problem_id) ON DELETE CASCADE ON UPDATE CASCADE,
                           FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                           PRIMARY KEY (course_id, assignment_id, problem_id, user_id, submission_id)
                        );''')

    sql_commands.append('''CREATE TABLE IF NOT EXISTS scores (
                             course_id integer NOT NULL,
                             assignment_id integer NOT NULL,
                             problem_id integer NOT NULL,
                             user_id text NOT NULL,
                             score real NOT NULL,
                           FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE,
                           FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE ON UPDATE CASCADE,
                           FOREIGN KEY (problem_id) REFERENCES problems (problem_id) ON DELETE CASCADE ON UPDATE CASCADE,
                           FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                           PRIMARY KEY (course_id, assignment_id, problem_id, user_id)
                        );''')

    sql_commands.append('''CREATE TABLE IF NOT EXISTS user_assignment_start (
                             user_id text NOT NULL,
                             course_id text NOT NULL,
                             assignment_id text NOT NULL,
                             start_time timestamp NOT NULL,
                           FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE,
                           FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE ON UPDATE CASCADE,
                           FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE
                        );''')

    return sql_commands

# Returns the number of non-admin, non-instructor, non-assistant students
# in a given course.
def students_course(course_id):
    return f'''SELECT user_id
               FROM course_registrations
               WHERE course_id = {course_id}'''

# Identifies which exercises are visible for a given course.
def visible_exercises_course(course_id):
    return f'''SELECT assignment_id, exercise_id, title
               FROM exercises
               WHERE course_id = {course_id}
                 AND visible = 1'''

# Calculates the number of exercises are visible for a given course.
def num_visible_exercises_course(course_id):
    return f'''SELECT assignment_id, COUNT(exercise_id) as exercise_count
               FROM ({visible_exercises_course(course_id)})
               GROUP BY assignment_id'''

# Identifies which assignments are visible for a given course.
def visible_assignments_course(course_id):
    return f'''SELECT assignment_id, title
               FROM assignments
               WHERE course_id = {course_id}
                 AND visible = 1'''

# Identifies whether each student has passed each exercise that they have attempted
# for a given course.
def user_exercise_status_course(course_id):
    return f'''SELECT s.assignment_id, s.exercise_id, s.user_id, MAX(s.passed) AS passed
               FROM submissions s
               INNER JOIN ({visible_exercises_course(course_id)}) e
                 ON s.assignment_id = e.assignment_id
                 AND s.exercise_id = e.exercise_id
               INNER JOIN ({visible_assignments_course(course_id)}) a
                 ON s.assignment_id = a.assignment_id
               INNER JOIN ({students_course(course_id)}) st
                 ON s.user_id = st.user_id
               WHERE s.course_id = {course_id}
               GROUP BY s.assignment_id, s.exercise_id, s.user_id'''

# Calculates the average score across all students for each assignment in a course,
# as well as the number of students who have completed each assignment and the number
# of students total for the course.
def assignment_summary_course(course_id):
    return f'''WITH const
               AS (SELECT COUNT(*) AS num_students FROM ({students_course(course_id)}))

               SELECT a.assignment_id,
                      a.title,
                      IFNULL(b.num_passed, 0) AS num_students_completed,
                      const.num_students AS num_students,
                      ROUND(IFNULL(b.total_percent, 0) / const.num_students, 1) AS avg_score
               FROM ({visible_assignments_course(course_id)}) a, const
               LEFT JOIN
               (
                 SELECT assignment_id, SUM(percent_passed > 0) AS num_passed, SUM(percent_passed) AS total_percent
                 FROM
                 (
                   SELECT sc.assignment_id, sc.user_id, SUM(sc.score) / nve.exercise_count AS percent_passed
                   FROM ({students_course(course_id)}) st
                   LEFT JOIN scores sc
                     ON st.user_id = sc.user_id
                   INNER JOIN ({num_visible_exercises_course(course_id)}) nve
                     ON sc.assignment_id = nve.assignment_id
                   GROUP BY sc.assignment_id, sc.user_id
                 )
               GROUP BY assignment_id
               ) b
                 ON a.assignment_id = b.assignment_id'''
