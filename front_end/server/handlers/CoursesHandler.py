# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class CoursesHandler(BaseUserHandler):
    async def get(self):
        try:
            # First, we check whether this is the first time the app
            # is being accessed. If so, make this user an admin.
            user_count = self.get_content_cookie("user_count", 30)
            if user_count:
                user_count = int(user_count)
            else:
                user_count = self.set_content_cookie("user_count", self.content.get_user_count(), 30)

            if user_count == 1 and not self.content.administrator_exists():
                self.content.add_admin_permissions(self.get_current_user())
                self.clear_cookie("is_administrator")
                self.redirect(f"/courses")

            if len(self.courses) == 0:
                if self.is_administrator:
                    self.redirect("/edit_course/")
                else:
                    self.redirect("/available")
            else:
                self.render("courses.html", registered_courses=self.courses, user_info=self.user_info, is_administrator=self.is_administrator)
        except Exception as inst:
            render_error(self, traceback.format_exc())