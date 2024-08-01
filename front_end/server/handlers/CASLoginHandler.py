# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseOtherHandler import *
from tornado.web import *
from tornado.auth import GoogleOAuth2Mixin
from content import *

# https://github.com/apereo/cas-sample-python-webapp/blob/master/app.py
# See https://djangocas.dev/blog/python-cas-flask-example/
class CASLoginHandler(BaseOtherHandler):
    async def get(self):
        try:
            if self.in_production_mode():
                service_url = f"https://{self.settings_dict['domain']}/caslogin?next=%2Fcourses"
            else:
                raise Exception("You cannot authenticate with CAS in development mode")
                #service_url="http://codebuddy.ls.byu.edu:8008/login?next=%2Flogin"

            server_url = "https://cas.byu.edu/cas/"

            # Moved this here so we can run it locally without having CAS installed.
            from cas import CASClient
            cas_client = CASClient(version=3, service_url=service_url, server_url=server_url)

            ticket = self.get_argument('ticket', False)
            if not ticket:
                cas_login_url = cas_client.get_login_url()
                self.redirect(cas_login_url)

            user_id, attributes, pgtiou = cas_client.verify_ticket(ticket)

            if not user_id:
                return

            user_dict = {"name": attributes["preferredFirstName"] + " " + attributes["preferredSurname"], "given_name": attributes["preferredFirstName"], "family_name": attributes["preferredSurname"], "locale": "en", "email_address": attributes["emailAddress"]}

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
        except Exception as inst:
            user_id_cookie = self.get_secure_cookie("user_id")
            if user_id_cookie:
                self.clear_cookie("user_id")

            render_error(self, traceback.format_exc())