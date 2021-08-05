import sys
sys.path.append("..")
from StaticFileHandler import *
from helper import *
import traceback
from BaseUserHandler import *
from content import *


settings_dict = load_yaml_dict(read_file("/Settings.yaml"))
content = Content(settings_dict)

class DownloadAllScoresHandler(BaseUserHandler):
    def get(self, course):
        course_basics = content.get_course_basics(course)
        descriptor = f"Course_{course_basics['title'].replace(' ', '_')}_Scores"
        temp_dir_path, zip_file_name, zip_file_path = content.create_zip_file_path(descriptor)

        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):

                content.create_export_paths(temp_dir_path, descriptor)

                assignments = content.get_assignments(course)
                for assignment in assignments:
                    file_contents = content.create_scores_text(course, assignment[0])
                    with open(f"{temp_dir_path}/{assignment[0]}.csv", "w") as score_file:
                        score_file.write(file_contents)

                content.zip_export_files(temp_dir_path, zip_file_name, zip_file_path, descriptor)
                zip_bytes = read_file(zip_file_path, "rb")

                self.set_header("Content-type", "application/zip")
                self.set_header("Content-Disposition", f"attachment; filename={zip_file_name}")
                self.write(zip_bytes)
                self.finish()
            else:
                self.render("permissions.html")

        except Exception as inst:
            render_error(self, traceback.format_exc())
        finally:
            content.remove_export_paths(zip_file_path, tmp_dir_path)

