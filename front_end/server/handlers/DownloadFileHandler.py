from BaseUserHandler import *

class DownloadFileHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id, exercise_id, file_name):
        try:
            course_basics = await self.get_course_basics(course_id)
            assignment_basics = await self.get_assignment_basics(course_basics, assignment_id)

            file_contents = (await self.get_exercise_details(course_basics, assignment_basics, exercise_id))["data_files"][file_name]
            self.set_header("Content-type", "application/octet-stream")
            self.set_header("Content-Disposition", "attachment")
            self.write(file_contents)
        except Exception as inst:
            self.write(traceback.format_exc())