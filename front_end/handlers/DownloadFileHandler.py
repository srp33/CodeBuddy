import traceback
from BaseUserHandler import *
from content import *


class DownloadFileHandler(BaseUserHandler):
    def get(self, course, assignment, exercise, file_name):
        try:
            file_contents = content.get_exercise_details(course, assignment, exercise)["data_files"][file_name]
            self.set_header("Content-type", "application/octet-stream")
            self.set_header("Content-Disposition", "attachment")
            self.write(file_contents)
        except Exception as inst:
            self.write(traceback.format_exc())

