# <copyright_statement>
#   CodeBuddy - A learning management system for computer programming
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class ExportAssignmentHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id):
        json_text = "An unknown error occurred."

        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)

                assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)
                assignment_details = await self.get_assignment_details(course_basics, assignment_id)

                exercises = {}
                for exercise in self.content.get_exercises(course_basics, assignment_basics):
                    # exercise_basics = self.content.get_exercise_basics(course_basics, assignment_basics, exercise[0])
                    exercise_basics = exercise[1]
                    del exercise_basics["id"]
                    del exercise_basics["exists"]
                    del exercise_basics["assignment"]

                    exercise_details = await self.get_exercise_details(course_basics, assignment_basics, exercise[0])

                    for test_title in exercise_details["tests"]:
                        del exercise_details["tests"][test_title]["test_id"]

                    exercises[exercise_basics["title"]] = {"basics": exercise_basics, "details": exercise_details}

                del assignment_basics["id"]
                del assignment_basics["exists"]
                del assignment_basics["course"]

                assignment_dict = {
                    "version": read_file('../VERSION').rstrip("\n"),
                    "basics": assignment_basics,
                    "details": assignment_details,
                    "exercises": exercises
                }

                # This package is needed because the base json package does not escape HTML characters.
                json_text = ujson.dumps(assignment_dict, default=str, encode_html_chars=True)
            else:
                json_text += " You do not have permission to perform this operation."
        except Exception as inst:
            json_text += " " + traceback.format_exc()

        self.set_header('Content-type', "application/json")
        self.write(json_text)
        self.finish()