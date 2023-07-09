from BaseUserHandler import *

class RemoveInstructorHandler(BaseUserHandler):
    async def get(self, course_id, user_id):
        message = "Error: You do not have permission to perform that task."

        try:
            if self.is_administrator or user_id == self.get_current_user():
                if self.content.user_has_role(user_id, course_id, "instructor"):
                    self.content.remove_course_permissions(course_id, user_id, "instructor")

                message = "Success"
        except Exception as inst:
            message = f"Error: {traceback.format_exc()}"

        self.write(message)