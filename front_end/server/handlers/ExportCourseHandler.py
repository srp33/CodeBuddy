from BaseUserHandler import *

class ExportCourseHandler(BaseUserHandler):
    def get(self, course):
        course_basics = self.get_course_basics(course)

        descriptor = f"Course_{course_basics['title'].replace(' ', '_')}"
        temp_dir_path, zip_file_name, zip_file_path = self.content.create_zip_file_path(descriptor)

        try:
            self.content.create_export_paths(temp_dir_path, descriptor)

            for table_name in ["courses", "assignments", "exercises"]:
                self.content.export_data(course_basics, table_name, f"{temp_dir_path}/{descriptor}/{table_name}.json")

            self.content.zip_export_files(temp_dir_path, zip_file_name, zip_file_path, descriptor)
            zip_bytes = read_file(zip_file_path, "rb")

            self.set_header("Content-type", "application/zip")
            self.set_header("Content-Disposition", f"attachment; filename={zip_file_name}")
            self.write(zip_bytes)
            self.finish()

        except Exception as inst:
            render_error(self, traceback.format_exc())
        finally:
            self.content.remove_export_paths(zip_file_path, tmp_dir_path)

