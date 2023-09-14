# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class AddAdminHandler(BaseUserHandler):
    async def get(self, user_id):
        message = "Error: You do not have permission to perform that task."

        try:
            if self.is_administrator:
                if self.content.user_exists(user_id) and not self.content.is_administrator(user_id):
                    self.content.add_admin_permissions(user_id)
                    message = "Success"
                else:
                    result = f"Error: The user '{user_id}' does not exist."
        except Exception as inst:
            message = f"Error: {traceback.format_exc()}"

        self.write(message)