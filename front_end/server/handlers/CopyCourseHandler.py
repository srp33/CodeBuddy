# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class CopyCourseHandler(BaseUserHandler):
    async def post(self, course_id):
        result = ""

        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id):
                new_title = self.get_body_argument("new_title").strip()
                existing_titles = list(map(lambda x: x[1]["title"], self.courses))

                if new_title in existing_titles:
                    result = "Error: A course with that title already exists."
                else:
                    course_basics = await self.get_course_basics(course_id)
                    await self.content.copy_course(course_basics, new_title)
            else:
                result = "You do not have permission to perform this task."
        except Exception as inst:
            result = f"Error: {traceback.format_exc()}"

        self.write(result)