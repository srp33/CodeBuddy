import atexit
import sqlite3
import sys
import traceback

sys.path.append('./server')
from helper import *
from content import *

settings_dict = load_yaml_dict(read_file("../Settings.yaml"))
content = Content(settings_dict)

version = read_file("../VERSION").rstrip()

# This tells us whether the migration has already happened.
check_sql = '''SELECT COUNT(*) AS count
               FROM tests
               WHERE exercise_id = 4251
                 AND txt_output LIKE 'Parsed with column specification%' '''

if content.fetchone(check_sql)["count"] > 0:
    print("***NotNeeded***")
else:
    sql = '''SELECT course_id, assignment_id, exercise_id
             FROM exercises
             WHERE back_end = 'r' AND solution_code LIKE '%read_%' '''

    for row in content.fetchall(sql):
        course_id = row["course_id"]
        assignment_id = row["assignment_id"]
        exercise_id = row["exercise_id"]

        print(f"Updating tests for {course_id}, {assignment_id}, {exercise_id}")

        exercise_details = content.get_exercise_details(course_id, assignment_id, exercise_id)
        exec_response = exec_code(settings_dict, exercise_details["solution_code"], "", exercise_details)

        for test_title in exec_response["test_outputs"]:
            txt_output = exec_response["test_outputs"][test_title]["txt_output"]

            sql = '''UPDATE tests
                     SET txt_output = ?
                     WHERE course_id = ?
                       AND assignment_id = ?
                       AND exercise_id = ?
                       AND title = ?'''

            content.execute(sql, (txt_output, course_id, assignment_id, exercise_id, test_title, ))

    print("***Success***")
