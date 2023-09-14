# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class ManageUsersHandler(BaseUserHandler):
    async def get(self):
        try:
            if self.is_administrator:
                self.render("manage_users.html", user_info=self.user_info, is_administrator=self.is_administrator)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def post(self):
        result = {"message": "", "users": []}

        try:
            pattern = self.request.body.decode()

            result["users"] = self.content.get_users_to_manage(f"%{pattern}%")
        except Exception as inst:
            result["message"] = traceback.format_exc()

        self.write(json.dumps(result, default=str))