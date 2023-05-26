from BaseUserHandler import *

class DownloadFileHandler(BaseUserHandler):
    def get(self, course, assignment, exercise, file_name):
        try:
            course_basics = self.get_course_basics(course)
            assignment_basics = self.get_assignment_basics(course_basics, assignment)

            file_contents = self.get_exercise_details(course_basics, assignment_basics, exercise)["data_files"][file_name]
            self.set_header("Content-type", "application/octet-stream")
            self.set_header("Content-Disposition", "attachment")
            self.write(file_contents)
        except Exception as inst:
            self.write(traceback.format_exc())

