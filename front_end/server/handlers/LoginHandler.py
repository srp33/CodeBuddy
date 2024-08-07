# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseOtherHandler import *
from tornado.web import *
from helper import *

class LoginHandler(BaseOtherHandler):
    async def get(self):
        try:
            # Google authentication is always enabled. BYU is only enabled if this (hidden) feature is specified.
            self.render("choose_login_option.html", byu_authentication=self.application.settings["byu_authentication"])
        except Exception as inst:
            render_error(self, traceback.format_exc())