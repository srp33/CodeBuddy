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
               FROM pragma_table_info("assignments")
               WHERE name = "has_timer"'''

cursor.execute(check_sql)
check_result = cursor.fetchone()["count"]

if check_result > 0:
    print("NotNeeded")
else:
    alter_sql_list = ['ALTER TABLE assignments ADD COLUMN start_date timestamp',
                      'ALTER TABLE assignments ADD COLUMN due_date timestamp',
                      'ALTER TABLE assignments ADD COLUMN allow_late integer',
                      'ALTER TABLE assignments ADD COLUMN view_answer_late integer',
                      'ALTER TABLE assignments ADD COLUMN late_percent real',
                      'ALTER TABLE assignments ADD COLUMN has_timer int NOT NULL DEFAULT 0',
                      'ALTER TABLE assignments ADD COLUMN hour_timer int',
                      'ALTER TABLE assignments ADD COLUMN minute_timer int',

                    '''CREATE TABLE IF NOT EXISTS scores (
                        course_id integer NOT NULL,
                        assignment_id integer NOT NULL,
                        problem_id integer NOT NULL,
                        user_id text NOT NULL,
                        score real NOT NULL,
                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE,
                        FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE,
                        FOREIGN KEY (problem_id) REFERENCES problems (problem_id) ON DELETE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                        PRIMARY KEY (course_id, assignment_id, problem_id, user_id))''',

                    '''CREATE TABLE IF NOT EXISTS user_assignment_start (
                        user_id text NOT NULL,
                        course_id text NOT NULL,
                        assignment_id text NOT NULL,
                        start_time timestamp NOT NULL,
                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE,
                        FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE)'''
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