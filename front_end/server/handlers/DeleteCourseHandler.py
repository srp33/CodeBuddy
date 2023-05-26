from BaseUserHandler import *

class DeleteCourseHandler(BaseUserHandler):
    def post(self, course):
        result = ""

        try:
            if self.is_administrator or self.is_instructor_for_course(course):
                self.content.delete_course(course)
            else:
                result = "You do not have permission to perform this task."
        except Exception as inst:
            result = traceback.format_exc()

        self.write(result)
