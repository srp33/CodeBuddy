# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class StudentScoreHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id, exercise_id, student_id, score):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                self.content.save_exercise_score(course_id, assignment_id, exercise_id, student_id, score)
                self.write(f"The score was successfully updated to {score}.")
            else:
                self.write("Error: You do not have permission to modify scores for this course.")
        except:
            self.write(f"Error: An error occurred when attempting to update the score, so it has not been updated. {traceback.format_exc()}")