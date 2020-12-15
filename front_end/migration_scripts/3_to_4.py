import atexit
import sqlite3
import traceback
#################
import sys
sys.path.append('/app')
from helper import *

settings_dict = load_yaml_dict(read_file("/Settings.yaml"))

conn = sqlite3.connect(f"/database/{settings_dict['db_name']}", isolation_level=None, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys=ON")

atexit.register(conn.close)
atexit.register(cursor.close)

version = read_file("/VERSION").rstrip()

# This tells us whether the migration has already happened.
check_sql = '''SELECT COUNT(*) AS count
               FROM pragma_table_info("courses")
               WHERE name = "passcode"'''

cursor.execute(check_sql)
check_result = cursor.fetchone()["count"]

if check_result > 0:
    print("NotNeeded")
else:
    alter_sql_list = ['ALTER TABLE courses ADD COLUMN passcode text',

                    '''CREATE TABLE IF NOT EXISTS course_registration (
                        user_id text NOT NULL,
                        course_id integer NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE)''',   

                    '''CREATE TABLE IF NOT EXISTS users2 (
                        user_id text PRIMARY KEY,
                        name text,
                        given_name text,
                        family_name text,
                        picture text,
                        locale text,
                        ace_theme text NOT NULL DEFAULT "tomorrow")''',

                    '''INSERT INTO users2
                       SELECT user_id
                       FROM users''',

                      'DROP TABLE IF EXISTS users',
                      'ALTER TABLE users2 RENAME TO users'

                    '''CREATE TABLE IF NOT EXISTS permissions2 (
                        user_id text NOT NULL,
                        role text NOT NULL,
                        course_id integer,
                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE)''',

                    '''INSERT INTO permissions2
                       SELECT user_id, role, course_id
                       FROM permissions''',

                      'DROP TABLE IF EXISTS permissions',
                      'ALTER TABLE permissions2 RENAME TO permissions'

                    '''CREATE TABLE IF NOT EXISTS problems2 (
                        course_id integer NOT NULL,
                        assignment_id integer NOT NULL,
                        problem_id integer PRIMARY KEY AUTOINCREMENT,
                        title text NOT NULL,
                        visible integer NOT NULL,
                        answer_code text NOT NULL,
                        answer_description text,
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
                        show_expected integer NOT NULL,
                        show_test_code integer NOT NULL,
                        test_code text,
                        date_created timestamp NOT NULL,
                        date_updated timestamp NOT NULL,
                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE ON UPDATE CASCADE)''',

                    '''INSERT INTO problems2
                       SELECT course_id, assignment_id, problem_id, title, visible, answer_code, answer_description, max_submissions, credit,
                       data_url, data_file_name, data_contents, back_end, expected_text_output, expected_image_output, instructions, output_type,
                       show_answer, show_expected, show_test_code, test_code, date_created, date_updated
                       FROM problems''',

                      'DROP TABLE IF EXISTS problems',
                      'ALTER TABLE problems2 RENAME TO problems'
                     ]

    error_occurred = False
    for sql in alter_sql_list:
        try:
            cursor.execute(sql)
        except:
            print(sql)
            print(traceback.format_exc())
            error_occurred = True

    if not error_occurred:
        print("Success")