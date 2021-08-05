import sys
sys.path.append("..")
from StaticFileHandler import *
from helper import *
import traceback
from BaseUserHandler import *
from content import *

settings_dict = load_yaml_dict(read_file("/Settings.yaml"))
content = Content(settings_dict)

class ExportCourseHandler(BaseUserHandler):
    def get(self, course):
        course_basics = content.get_course_basics(course)

        descriptor = f"Course_{course_basics['title'].replace(' ', '_')}"
        temp_dir_path, zip_file_name, zip_file_path = content.create_zip_file_path(descriptor)

        try:
            content.create_export_paths(temp_dir_path, descriptor)

            for table_name in ["courses", "assignments", "exercises"]:
                content.export_data(course_basics, table_name, f"{temp_dir_path}/{descriptor}/{table_name}.json")

            content.zip_export_files(temp_dir_path, zip_file_name, zip_file_path, descriptor)
            zip_bytes = read_file(zip_file_path, "rb")

            self.set_header("Content-type", "application/zip")
            self.set_header("Content-Disposition", f"attachment; filename={zip_file_name}")
            self.write(zip_bytes)
            self.finish()

        except Exception as inst:
            render_error(self, traceback.format_exc())
        finally:
            content.remove_export_paths(zip_file_path, tmp_dir_path)

