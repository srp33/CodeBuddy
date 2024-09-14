# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from tornado.concurrent import Future
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
        self.content = Content(self.settings_dict)

    def get_current_user(self):
        user_id = self.get_secure_cookie("user_id")

        if user_id:
            return user_id.decode()
        
    def on_finish(self):
        self.content.close()
        return super().on_finish()

    ###############################################
    # Helper functions
    ###############################################

    def in_production_mode(self):
        return self.settings_dict["mode"] == "production"