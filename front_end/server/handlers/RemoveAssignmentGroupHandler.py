# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class RemoveAssignmentGroupHandler(BaseUserHandler):
    async def get(self, course_id, assignment_group_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                self.content.remove_assignment_group(course_id, assignment_group_id)

                return self.write("Success")
            else:
                return self.write("Error: You do not have permission to perform this task.")
        except Exception as inst:
            return self.write(f"Error: {traceback.format_exc()}")