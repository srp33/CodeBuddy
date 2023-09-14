# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *
import datetime as dt

class ViewAtRiskStudentsHandler(BaseUserHandler):
    async def get(self, course_id, recent_submissions_days_threshold):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)

                self.render("view_at_risk_students.html", num_registered_students=len(self.content.get_registered_students(course_id)), num_submissions=await self.content.get_num_course_submissions(course_id), students_no_recent_submissions=self.content.get_students_no_recent_submissions(course_id, recent_submissions_days_threshold), recent_submissions_days_threshold=int(recent_submissions_days_threshold), course_basics=course_basics, courses=self.courses, user_info=self.user_info, is_administrator=self.is_administrator)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())