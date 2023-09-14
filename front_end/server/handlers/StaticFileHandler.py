# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from tornado.web import *

class StaticFileHandler(RequestHandler):
    async def get(self, file_name):
        if file_name.endswith(".html"):
            try:
                self.render(file_name)
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            content_type = "text/css"
            read_mode = "r"

            if file_name.endswith(".js"):
                content_type = "text/javascript"
            elif file_name.endswith(".png"):
                content_type = "image/png"
                read_mode = "rb"
            elif file_name.endswith(".ico"):
                content_type = "image/x-icon"
                read_mode = "rb"
            elif file_name.endswith(".webmanifest"):
                content_type = "application/json"

            file_contents = read_file("/static/{}".format(file_name), mode=read_mode)

            self.set_header('Content-type', content_type)
            self.write(file_contents)