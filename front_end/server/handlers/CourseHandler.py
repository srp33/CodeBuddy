# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class CourseHandler(BaseUserHandler):
    async def get(self, course_id):
        try:
            course_basics = await self.get_course_basics(course_id)

            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                assignment_statuses = await self.get_assignment_statuses(course_basics, show_hidden=True)

                assignment_summary_scores=self.content.get_assignment_summary_scores(course_id)

                self.render("course_admin.html", courses=self.courses, course_basics=course_basics, course_details=await self.get_course_details(course_id, True), assignment_statuses=assignment_statuses, assignment_summary_scores=assignment_summary_scores, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_assistant=await self.is_assistant_for_course(course_id))
            else:
                user_is_registered = False
                for course in self.courses:
                    if int(course_id) == course[0]:
                        user_is_registered = True

                if user_is_registered:
                    assignment_statuses = await self.get_assignment_statuses(course_basics)
                    has_any_custom_scoring = len([x for x in assignment_statuses if x[1]["custom_scoring"] != ""]) > 0

                    self.render("course.html", courses=self.courses, assignment_statuses=assignment_statuses, has_any_custom_scoring=has_any_custom_scoring, course_basics=course_basics, course_details=await self.get_course_details(course_id, True), curr_datetime=get_current_datetime(), user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id))
                else:
                    self.render("unavailable_course.html", courses=self.courses, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id))
        except Exception as inst:
            render_error(self, traceback.format_exc())