# <copyright_statement>
#   CodeBuddy - A learning management system for computer programming
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

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
               WHERE exercise_id = 4287
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
