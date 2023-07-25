# <copyright_statement>
#   CodeBuddy - A learning management system for computer programming
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from content import *
from helper import *
from tornado.web import RequestHandler

class BaseRequestHandler(RequestHandler):
    ###############################################
    # Overriding functions
    ###############################################

    def prepare(self):
        super().prepare()

        self.settings_dict = load_yaml_dict(read_file("../Settings.yaml"))
        self.content = Content()

    def get_current_user(self):
        user_id = self.get_secure_cookie("user_id")

        if user_id:
            return user_id.decode()

    ###############################################
    # Helper functions
    ###############################################

    def in_production_mode(self):
        return self.settings_dict["mode"] == "production"