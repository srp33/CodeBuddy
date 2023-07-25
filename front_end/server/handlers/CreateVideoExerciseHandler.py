# <copyright_statement>
#   CodeBuddy - A learning management system for computer programming
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *
import datetime as dt

class CreateVideoExerciseHandler(BaseUserHandler):
    async def post(self, course_id, assignment_id):
        result = ""

        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)
                assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)

                exercise_basics = self.content.get_exercise_basics(course_basics, assignment_basics, None)
                exercise_details = await self.get_exercise_details(course_basics, assignment_basics, None)

                exercise_basics["title"] = self.get_body_argument("title")
                exercise_details["instructions"] = self.get_body_argument("instructions")
                exercise_details["back_end"] = "not_code"
                exercise_details["allow_any_response"] = True
                created_date = dt.datetime.utcnow()
                exercise_details["date_updated"] = created_date
                exercise_details["date_created"] = created_date

                exercise = self.content.save_exercise(exercise_basics, exercise_details)
            else:
                result = "You do not have permissions to perform this operation."
        except Exception as inst:
            result = traceback.format_exc()

        self.write(result);