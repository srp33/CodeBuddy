import atexit
import sqlite3
import sys
import traceback

sys.path.append('./server')
from helper import *
from content import *

settings_dict = load_yaml_dict(read_file("../Settings.yaml"))
content = Content(settings_dict)

version = read_file("VERSION").rstrip()

# This tells us whether the migration has already happened.
check_sql = '''SELECT COUNT(*) AS count
               FROM pragma_table_info("test_submissions")'''

if content.fetchone(check_sql)["count"] > 0:
    print("***NotNeeded***")
else:
    with open("migration_scripts/24_to_25.sql") as sql_file:
        sql_statements = sql_file.read().split(";")

        for sql in sql_statements:
            content.execute(sql)

        sql = '''SELECT e.exercise_id, t.test_id, t.title
                 FROM tests t
                 INNER JOIN exercises e
                   ON t.course_id = e.course_id
                  AND t.assignment_id = e.assignment_id
                  AND t.exercise_id = e.exercise_id
                 ORDER by e.exercise_id, t.test_id'''

        test_dict = {}
        for row in content.fetchall(sql):
            exercise_id = row["exercise_id"]
            test_id = row["test_id"]
            title = row["title"]

            if exercise_id not in test_dict:
                test_dict[exercise_id] = []

            test_dict[exercise_id].append([test_id, title])

        for exercise_id, tests in test_dict.items():
            for i in range(len(tests)):
                test_id = tests[i][0]
                title = tests[i][1]

                if title == "":
                    title = f"Test {i+1}"

                    sql = '''UPDATE tests
                             SET title = ?
                             WHERE test_id = ?'''

                    print(f"Updating title to {title} for exercise {exercise_id}, test {test_id}")
                    content.execute(sql, (title, test_id, ))

        sql = '''SELECT course_id, assignment_id, exercise_id
                 FROM exercises
                 WHERE output_type = 'jpg'
                   AND back_end = 'python' OR back_end = 'python_script' '''

        ids = []
        for row in content.fetchall(sql):
            ids.append([row["course_id"], row["assignment_id"], row["exercise_id"]])

        for x in ids:
            exercise_details = content.get_exercise_details(x[0], x[1], x[2])
            exec_response = exec_code(settings_dict, exercise_details["solution_code"], "", exercise_details)

            for test_title in exec_response["test_outputs"]:
                txt_output = exec_response["test_outputs"][test_title]["txt_output"]
                jpg_output = exec_response["test_outputs"][test_title]["jpg_output"]

                sql = '''UPDATE tests
                         SET txt_output = ?, jpg_output = ?
                         WHERE course_id = ?
                           AND assignment_id = ?
                           AND exercise_id = ?
                           AND title = ?'''

                content.execute(sql, (txt_output, jpg_output, x[0], x[1], x[2], test_title, ))

        print("***Success***")
