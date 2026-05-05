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
                assignment_groups = self.content.get_assignment_groups(course_id)

                assignment_summary_scores=self.content.get_assignment_summary_scores(course_id)

                self.render("course_admin.html", courses=self.courses, course_basics=course_basics, course_details=await self.get_course_details(course_id, True), assignment_statuses=assignment_statuses, assignment_groups=assignment_groups, assignment_summary_scores=assignment_summary_scores, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_assistant=await self.is_assistant_for_course(course_id))
            else:
                user_is_registered = False
                for course in self.courses:
                    if int(course_id) == course[0]:
                        user_is_registered = True

                if user_is_registered:
                    assignment_statuses = await self.get_assignment_statuses(course_basics)
                    assignment_groups = self.content.parse_assignment_groups(assignment_statuses)

                    has_any_custom_scoring = len([x for x in assignment_statuses if x[2]["custom_scoring"] != ""]) > 0

                    group_statuses = {}
                    for group in assignment_groups:
                        group_title = group[0]
                        group_assignments = [a for a in assignment_statuses if a[1] == group_title]
                        if len(group_assignments) == 0:
                            group_statuses[group_title] = "not_started"
                        elif all(a[2]["completed"] or a[2]["timer_has_ended"] for a in group_assignments):
                            group_statuses[group_title] = "completed"
                        elif all(not a[2]["completed"] and not a[2]["timer_has_ended"] and not a[2]["in_progress"] and a[2]["num_completed"] == 0 for a in group_assignments):
                            group_statuses[group_title] = "not_started"
                        else:
                            group_statuses[group_title] = "in_progress"

                    self.render("course.html", courses=self.courses, assignment_statuses=assignment_statuses, assignment_groups=assignment_groups, has_any_custom_scoring=has_any_custom_scoring, group_statuses=group_statuses, course_basics=course_basics, course_details=await self.get_course_details(course_id, True), curr_datetime=get_current_datetime(), user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id))
                else:
                    self.render("unavailable_course.html", courses=self.courses, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id))
        except Exception as inst:
            render_error(self, traceback.format_exc())