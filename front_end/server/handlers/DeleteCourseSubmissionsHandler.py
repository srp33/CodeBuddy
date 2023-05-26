from BaseUserHandler import *

class DeleteCourseSubmissionsHandler(BaseUserHandler):
    def post(self, course):
        try:
            result = ""

            if self.is_administrator or self.is_instructor_for_course(course):
                self.content.delete_course_submissions(course)
            else:
                result = "You do not have permission to complete this task."
        except Exception as inst:
            result = traceback.format_exc()

        self.write(result)

