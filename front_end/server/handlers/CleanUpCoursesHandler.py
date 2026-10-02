# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *


class CleanUpCoursesHandler(BaseUserHandler):
    async def get(self):
        try:
            if self.is_administrator:
                all_courses = self.content.get_all_courses_for_clean_up_courses()
                self.render("clean_up_courses.html", courses=self.courses, all_courses=all_courses, user_info=self.user_info, is_administrator=self.is_administrator)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def post(self):
        try:
            if not self.is_administrator:
                return self.write("Error: You do not have permission to perform this task.")

            course_ids_raw = self.get_body_argument("course_ids", default="").strip()
            if not course_ids_raw:
                return self.write("Error: Please select at least one course.")

            course_ids = []
            for part in course_ids_raw.split(","):
                part = part.strip()
                if not part:
                    continue
                try:
                    course_ids.append(int(part))
                except ValueError:
                    return self.write("Error: Invalid course id.")

            if len(course_ids) == 0:
                return self.write("Error: Please select at least one course.")

            for course_id in course_ids:
                self.content.delete_course(course_id)
        except Exception as inst:
            return self.write(f"Error: {traceback.format_exc()}")
