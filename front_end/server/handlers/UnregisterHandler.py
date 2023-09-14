# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class UnregisterHandler(BaseUserHandler):
    async def get(self, course_id, user_id):
        result = "Error: No response"

        try:
            if self.get_current_user() == user_id or self.is_administrator or await self.is_instructor_for_course(course_id):

                title = (await self.get_course_basics(course_id))["title"]
                if self.content.is_user_registered(course_id, user_id):
                    self.content.unregister_user_from_course(course_id, user_id)
                    #TODO: Clear cookie for courses

                    result = f"Success: The user {user_id} has been removed from {title}"
                else:
                    result = f"Error: The user {user_id} is not currently registered for the course \"{title}\""
            else:
                result = f"Error: You do not have permissions to perform this task."
        except Exception as inst:
            result = f"Error: {traceback.format_exc()}"

        self.write(result)