# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *
import datetime as dt

class CourseHandler(BaseUserHandler):
    async def get(self, course_id):
        course_basics = await self.get_course_basics(course_id)

        if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
            try:
                assignments = self.content.get_assignments(course_basics)

                self.render("course_admin.html", courses=self.courses, assignments=assignments, assignment_statuses=await self.content.get_assignment_statuses(course_id, self.get_current_user(), True), course_basics=course_basics, course_details=await self.get_course_details(course_id, True), course_summary_scores=self.content.get_course_summary_scores(course_id, assignments), user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_assistant=await self.is_assistant_for_course(course_id))
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            try:
                user_is_registered = False
                for course in self.courses:
                    if int(course_id) == course[0]:
                        user_is_registered = True

                if user_is_registered:
                    self.render("course.html", courses=self.courses, assignments=await self.get_assignments(course_basics), assignment_statuses=await self.content.get_assignment_statuses(course_id, self.get_current_user(), False), course_basics=course_basics, course_details=await self.get_course_details(course_id, True), curr_datetime=dt.datetime.utcnow(), user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id))
                else:
                    self.render("unavailable_course.html", courses=self.courses, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id))
            except Exception as inst:
                render_error(self, traceback.format_exc())