# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class MoveAssignmentHandler(BaseUserHandler):
    async def post(self, course_id, assignment_id):
        result = ""

        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id):
                new_course_id = self.get_body_argument("new_course_id")
                existing_course_basics = await self.get_course_basics(course_id)
                new_course_basics = await self.get_course_basics(new_course_id)
                new_course_assignments = self.content.get_assignments(new_course_basics)
                current_assignment_basics = self.content.get_assignment_basics(existing_course_basics, assignment_id)

                if self.content.has_duplicate_title(new_course_assignments, None, current_assignment_basics["title"]):
                    result = f"Error: An assignment with the title <b>{current_assignment_basics['title']}</b> already exists in the <b>{new_course_basics['title']}</b> course."
                else:
                    self.content.move_assignment(course_id, assignment_id, new_course_id)
            else:
                result = "You do not have permission to move this assignment."
        except Exception as inst:
            result = traceback.format_exc()

        self.write(result)