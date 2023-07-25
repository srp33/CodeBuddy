# <copyright_statement>
#   CodeBuddy - A learning management system for computer programming
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class MoveExerciseHandler(BaseUserHandler):
    async def post(self, course_id, assignment_id, exercise_id):
        result = ""

        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id):
                existing_course_basics = await self.get_course_basics(course_id)
                existing_assignment_basics = self.content.get_assignment_basics(existing_course_basics, assignment_id)
                existing_exercise_basics = self.content.get_exercise_basics(existing_course_basics, existing_assignment_basics, exercise_id)

                new_assignment_id = self.get_body_argument("new_assignment_id")
                new_assignment_basics = self.content.get_assignment_basics(existing_course_basics, new_assignment_id)
                new_assignment_exercises = self.content.get_exercises(existing_course_basics, new_assignment_basics)


                if self.content.has_duplicate_title(new_assignment_exercises, None, existing_exercise_basics["title"]):
                    result = f"Error: An exercise with the title <b>{existing_exercise_basics['title']}</b> already exists in the <b>{new_assignment_basics['title']}</b> assignment."
                else:
                    self.content.move_exercise(course_id, assignment_id, exercise_id, new_assignment_id)
            else:
                result = "You do not have permission to move this exercise."
        except Exception as inst:
            result = traceback.format_exc()

        self.write(result)