# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class ViewStudentsHandler(BaseUserHandler):
    async def get(self, course_id):
        try:
            is_instructor = await self.is_instructor_for_course(course_id)

            if self.is_administrator or is_instructor:
                self.render("view_students.html", course_basics=await self.get_course_basics(course_id), students=self.content.get_registered_students(course_id), user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=is_instructor, is_assistant=await self.is_assistant_for_course(course_id))
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())