# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class ExportSubmissionsHandler(BaseUserHandler):
    async def get(self, course_id):
        course_basics = await self.get_course_basics(course_id)

        descriptor = f"Submissions_{course_basics['title'].replace(' ', '_')}"
        temp_dir_path, zip_file_name, zip_file_path = self.content.create_zip_file_path(descriptor)

        try:
            self.content.create_export_paths(temp_dir_path, descriptor)

            self.content.export_data(course_basics, "submissions", f"{temp_dir_path}/{descriptor}/submissions.json")

            self.content.zip_export_files(temp_dir_path, zip_file_name, zip_file_path, descriptor)
            zip_bytes = read_file(zip_file_path, "rb")

            self.set_header("Content-type", "application/zip")
            self.set_header("Content-Disposition", f"attachment; filename={zip_file_name}")
            self.write(zip_bytes)
            self.finish()

        except Exception as inst:
            render_error(self, traceback.format_exc())
        finally:
            self.content.remove_export_paths(zip_file_path, temp_dir_path)