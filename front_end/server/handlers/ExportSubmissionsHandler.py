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