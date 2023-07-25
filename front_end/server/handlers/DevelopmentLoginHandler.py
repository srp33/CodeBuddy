# <copyright_statement>
#   CodeBuddy - A learning management system for computer programming
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseOtherHandler import *
from content import *
from tornado.web import *

class DevelopmentLoginHandler(BaseOtherHandler):
    async def get(self):
        self.render("devlogin.html")

    async def post(self):
        try:
            user_id = self.get_body_argument("user_id")
            dev_password = self.get_body_argument("dev_password")

            if user_id == "":
                self.write("Invalid user ID.")
            else:
                if dev_password == self.settings_dict["dev_password"]:
                    # Add static information for test user.
                    user_dict = {'name': f'{user_id} TestUser', 'given_name': user_id, 'family_name': 'TestUser', 'locale': 'en', 'email_address': f'{user_id}@nospam.edu'}

                    if self.content.user_exists(user_id):
                        # Update user with current information when they already exist.
                        self.content.update_user(user_id, user_dict)
                    else:
                        # Store current user information when they do not already exist.
                        self.content.add_user(user_id, user_dict)

                    self.set_secure_cookie("user_id", user_id, expires_days=30)

                    redirect_path = self.get_secure_cookie("redirect_path")
                    self.clear_cookie("redirect_path")
                    if not redirect_path:
                        redirect_path = "/"
                    self.redirect(redirect_path)
                else:
                    self.write("Invalid password")
        except Exception as inst:
            render_error(self, traceback.format_exc())