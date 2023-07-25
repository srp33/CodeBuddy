# <copyright_statement>
#   CodeBuddy - A learning management system for computer programming
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class EditAssignmentScoresHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id, student_id):
        try:
            course_basics = await self.get_course_basics(course_id)
            assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)

            if self.is_administrator or await self.is_instructor_for_course(course_id):
                self.render("edit_assignment_scores.html", student_id=student_id, courses=self.courses, course_basics=course_basics, assignments=self.content.get_assignments(course_basics), assignment_basics=assignment_basics, exercise_statuses=self.content.get_exercise_statuses(course_id, assignment_id, student_id, show_hidden=False), result=None, user_info=self.user_info, is_administrator=self.is_administrator)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def post(self, course_id, assignment_id, student_id):
        try:
            course_basics = await self.get_course_basics(course_id)
            assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)

            if self.is_administrator or await self.is_instructor_for_course(course_id):
                exercise_statuses = self.content.get_exercise_statuses(course_id, assignment_id, student_id, show_hidden=False)
                result = ""
                for exercise in exercise_statuses:
                    student_score = self.get_body_argument(str(exercise[1]["id"]))
                    if (student_score.isnumeric()):
                        result = f"Success: {student_id}'s scores for this assignment have been updated."
                        self.content.save_exercise_score(course_id, assignment_id, exercise[1]["id"], student_id, int(student_score))
                    else:
                        result = "Error: Newly entered scores must be numeric."

                self.render("edit_assignment_scores.html", student_id=student_id, courses=self.courses, course_basics=course_basics, assignments=await self.get_assignments(course_basics), assignment_basics=assignment_basics, exercise_statuses=self.content.get_exercise_statuses(course_id, assignment_id, student_id, show_hidden=False), result=result, user_info=self.user_info, is_administrator=self.is_administrator)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())