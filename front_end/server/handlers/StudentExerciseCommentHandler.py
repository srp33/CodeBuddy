# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class StudentExerciseCommentHandler(BaseUserHandler):
    async def post(self, course_id, assignment_id, exercise_id, student_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                comment = self.request.body.decode("utf-8")
                saved_comment = self.content.save_exercise_comment(course_id, assignment_id, exercise_id, student_id, self.get_current_user(), comment)

                if saved_comment == "":
                    self.write("The comment was cleared.")
                else:
                    self.write("The comment was saved successfully.")
            else:
                self.write("Error: You do not have permission to leave comments for this course.")
        except:
            self.write(f"Error: An error occurred when attempting to save the comment. {traceback.format_exc()}")
