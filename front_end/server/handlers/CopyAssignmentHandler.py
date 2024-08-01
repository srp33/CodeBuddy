# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class CopyAssignmentHandler(BaseUserHandler):
    async def post(self, course_id, assignment_id):
        course_basics = await self.get_course_basics(course_id)
        result = ""

        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id):
                new_title = self.get_body_argument("new_title").strip()

                if new_title == "":
                    result = "The title cannot be blank."
                else:
                    existing_titles = list(map(lambda x: x[1]["title"], self.content.get_assignments(course_basics)))
                    if new_title in existing_titles:
                        result = "An assignment with that title already exists in this course."
                    else:
                        self.content.copy_assignment(course_id, assignment_id, new_title)
            else:
                result = "You do not have permission to copy this assignment."
        except Exception as inst:
            result = traceback.format_exc()

        self.write(result)