from BaseUserHandler import *

class DeleteCourseHandler(BaseUserHandler):
    async def post(self, course_id):
        result = ""

        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id):
                self.content.delete_course(course_id)
            else:
                result = "You do not have permission to perform this task."
        except Exception as inst:
            result = traceback.format_exc()

        self.write(result)