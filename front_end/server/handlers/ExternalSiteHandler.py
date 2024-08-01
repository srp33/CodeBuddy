# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *
import os
import urllib.request

class ExternalSiteHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id, encoded_url):
        try:
            url = urllib.parse.unquote(encoded_url)

            assignment_details = await self.get_assignment_details(await self.get_course_basics(course_id), assignment_id)

            if url not in assignment_details["allowed_external_urls"]:
                return self.write("Access to {url} is not allowed for this course")

            url_hash = md5_hash_string(url)
            cache_file_path = f"/tmp/{url_hash}"

            if os.path.exists(cache_file_path):
                with open(cache_file_path, "rb") as cache_file:
                    content = cache_file.read()
            else:
                content = urllib.request.urlopen(url).read()

                with open(cache_file_path, "wb") as cache_file:
                    cache_file.write(content)

            if url.endswith(".html"):
                self.set_header('Content-type', "text/html; charset=UTF-8")
            elif url.endswith(".pdf"):
                self.set_header('Content-type', "application/pdf")
            else:
                self.set_header('Content-type', 'application/octet-stream')

            self.write(content)
        except Exception as inst:
            return self.write(f"An error occurred when attempting to access {url}. {traceback.format_exc()}")