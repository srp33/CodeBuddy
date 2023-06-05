from BaseUserHandler import *

class DeleteCourseSubmissionsHandler(BaseUserHandler):
    async def post(self, course_id):
        try:
            result = ""

            if self.is_administrator or await self.is_instructor_for_course(course_id):
                self.content.delete_course_submissions(course_id)
            else:
                result = "You do not have permission to complete this task."
        except Exception as inst:
            result = traceback.format_exc()

        self.write(result)

