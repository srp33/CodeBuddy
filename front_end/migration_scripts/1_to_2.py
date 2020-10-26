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
               FROM pragma_table_info("problems")
               WHERE name = "expected_text_output"'''

cursor.execute(check_sql)
check_result = cursor.fetchone()["count"]

if check_result > 0:
    print("NotNeeded")
else:
    alter_sql_list = ['ALTER TABLE problems RENAME COLUMN expected_output TO expected_text_output',
                      'ALTER TABLE problems ADD COLUMN expected_image_output text NOT NULL DEFAULT ""',

                    '''UPDATE problems
                       SET expected_image_output = expected_text_output
                       WHERE output_type = "jpg"''',
                    '''UPDATE problems
                       SET expected_text_output = ""
                       WHERE output_type = "jpg"''',

                      'ALTER TABLE submissions RENAME COLUMN code_output TO text_output',
                      'ALTER TABLE submissions ADD COLUMN image_output text NOT NULL DEFAULT ""',

                    '''UPDATE submissions
                       SET image_output = text_output
                       WHERE problem_id IN (SELECT problem_id FROM problems WHERE output_type = "jpg")''',
                    '''UPDATE submissions
                       SET text_output = ""
                       WHERE problem_id IN (SELECT problem_id FROM problems WHERE output_type = "jpg")''',

                    '''CREATE TABLE IF NOT EXISTS submissions2 (
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
                         FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE,
                         FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE,
                         FOREIGN KEY (problem_id) REFERENCES problems (problem_id) ON DELETE CASCADE,
                         FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                         PRIMARY KEY (course_id, assignment_id, problem_id, user_id, submission_id))''',

                    '''INSERT INTO submissions2
                       SELECT course_id, assignment_id, problem_id, user_id, submission_id, code,
                              text_output, image_output, passed, date
                       FROM submissions''',

                      'DROP TABLE IF EXISTS submissions',
                      'ALTER TABLE submissions2 RENAME TO submissions'
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
