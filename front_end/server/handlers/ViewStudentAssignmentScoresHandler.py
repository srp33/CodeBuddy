# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class ViewStudentAssignmentScoresHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id, student_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)
                assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)
                student_info = self.content.get_user_info(student_id)
                exercise_statuses = self.content.get_exercise_statuses(course_id, assignment_id, student_id)

                self.render("view_student_assignment_scores.html", student_id=student_id, student_name=student_info["name"], courses=self.courses, course_basics=course_basics, assignment_statuses=await self.get_assignment_statuses(course_basics), assignment_basics=assignment_basics, exercise_statuses=exercise_statuses, result=None, user_info=self.user_info, is_administrator=self.is_administrator)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())