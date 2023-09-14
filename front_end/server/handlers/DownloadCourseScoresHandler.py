# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *
from datetime import datetime

class DownloadCourseScoresHandler(BaseUserHandler):
    async def get(self, course_id):
        course_basics = await self.get_course_basics(course_id)

        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                the_date = datetime.utcnow().strftime("%Yy_%mM_%dd_%Hh_%Mm_%Ss")
                out_file_prefix = re.sub(r"\W", "_", course_basics['title'])
                tsv_text = self.content.create_course_scores_text(course_basics)

                self.set_header("Content-Disposition", f"attachment; filename={out_file_prefix}_Scores_{the_date}.tsv")
                self.set_header('Content-type', "text/tab-separated-values")
                self.write(tsv_text)
            else:
                self.render("permissions.html")
        except Exception as inst:
            #self.write(traceback.format_exc())
            render_error(self, traceback.format_exc())


#    def get(self, course):
#        course_basics = self.content.get_course_basics(course)
#        descriptor = f"Course_{course_basics['title'].replace(' ', '_')}_Scores"
#        temp_dir_path, zip_file_name, zip_file_path = self.content.create_zip_file_path(descriptor)
#
#        try:
#            if self.is_administrator() or await self.is_instructor_for_course(course) or await self.is_assistant_for_course(course):
#
#                self.content.create_export_paths(temp_dir_path, descriptor)
#
#                assignments = self.content.get_assignments_basic(course)
#                for assignment in assignments:
#                    file_contents = self.content.create_scores_text(course, assignment[0])
#                    with open(f"{temp_dir_path}/{assignment[0]}.csv", "w") as score_file:
#                        score_file.write(file_contents)
#
#                self.content.zip_export_files(temp_dir_path, zip_file_name, zip_file_path, descriptor)
#                zip_bytes = read_file(zip_file_path, "rb")
#
#                self.set_header("Content-type", "application/zip")
#                self.set_header("Content-Disposition", f"attachment; filename={zip_file_name}")
#                self.write(zip_bytes)
#                self.finish()
#            else:
#                self.render("permissions.html")
#
#        except Exception as inst:
#            render_error(self, traceback.format_exc())
#        finally:
#            self.content.remove_export_paths(zip_file_path, tmp_dir_path)