# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class RemoveAssistantHandler(BaseUserHandler):
    async def get(self, course_id, user_id):
        message = "Error: You do not have permission to perform that task."

        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or user_id == self.get_current_user():
                if self.content.user_has_role(user_id, course_id, "assistant"):
                    self.content.remove_course_permissions(course_id, user_id, "assistant")

                message = "Success"
        except Exception as inst:
            message = f"Error: {traceback.format_exc()}"

        self.write(message)