from BaseUserHandler import *

class DeleteAssignmentHandler(BaseUserHandler):
    async def post(self, course_id, assignment_id):
        result = ""

        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id):
                self.content.delete_assignment(self.content.get_assignment_basics(await self.get_course_basics(course_id), assignment_id))
            else:
                result = "You do not have permission to delete this assignment."
        except Exception as inst:
            result = traceback.format_exc()

        self.write(result)
