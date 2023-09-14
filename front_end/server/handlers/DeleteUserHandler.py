# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class DeleteUserHandler(BaseUserHandler):
    def get(self, user_id):
        self.render("delete_user.html", user_id_to_delete=user_id, user_info=self.user_info, is_administrator=self.is_administrator)

    async def post(self, user_id):
        result = f"An error occurred when attempting to delete this user account: {user_id}."

        try:
            if self.content.user_exists(user_id):
                if self.is_administrator:
                    if user_id == self.get_current_user():
                        result = "You cannot delete your account because you are an administrator. You must first remove your administrator access."
                    else:
                        self.content.delete_user(user_id)
                        result = ""
                else:
                    if user_id == self.get_current_user():
                        self.content.delete_user(user_id)
                        result = ""
                    else:
                        result = "You do not have permission to delete another user's account."
            else:
                result += f" No user with that ID exists: {user_id}"
        except Exception as inst:
            result = f"An error occurred: {traceback.format_exc()}."

        self.write(result)