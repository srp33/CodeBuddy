# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class DiffHandler(BaseUserHandler):
    async def post(self):
        try:
            course_id = self.get_body_argument("course_id")
            assignment_id = self.get_body_argument("assignment_id")
            exercise_id = self.get_body_argument("exercise_id")
            expected_output = self.get_body_argument("expected_output", "")
            actual_output = self.get_body_argument("actual_output", "")
            diff_output = self.get_body_argument("diff_output", "")

            course_basics = await self.get_course_basics(course_id)
            assignment_basics = await self.get_assignment_basics(course_basics, assignment_id)
            exercise_basics = await self.get_exercise_basics(course_basics, assignment_basics, exercise_id)
            exercise_details = await self.get_exercise_details(course_basics, assignment_basics, exercise_id)

            if not course_basics["exists"] or not assignment_basics["exists"] or not exercise_basics["exists"]:
                render_error(self, "Sorry, the specified course, assignment, or exercise are not available.")
                return

            assignment_statuses = await self.get_assignment_statuses(course_basics)
            assignment_details = await self.get_assignment_details(course_basics, assignment_id)

            if not await self.check_whether_should_show_exercise(course_id, assignment_id, assignment_details, assignment_statuses, self.courses, assignment_basics, course_basics):
                return

            args = {"expected": expected_output, "actual": actual_output, "diff": diff_output}

            if exercise_details["output_type"] == "txt":
                self.render("diff_txt.html", **args)
            else:
                self.render("diff_jpg.html", **args)
        except Exception as inst:
            render_error(self, traceback.format_exc())