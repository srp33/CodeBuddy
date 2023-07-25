# <copyright_statement>
#   CodeBuddy - A learning management system for computer programming
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseOtherHandler import *
from tornado.web import *
from content import *
from helper import *

class HomeHandler(BaseOtherHandler):
    async def get(self):
        try:
            user_id = self.get_secure_cookie("user_id")

            if user_id:
                self.redirect(f"/courses")
            else:
                self.render("home.html")
        except Exception as inst:
            print(traceback.format_exc())
            render_error(self, traceback.format_exc())