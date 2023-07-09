from BaseUserHandler import *

class RemoveAdminHandler(BaseUserHandler):
    async def get(self):
        message = "Error: You do not have permission to perform that task."

        try:
            if self.is_administrator:
                self.content.remove_course_permissions(None, self.get_current_user(), "administrator")
                message = "Success"
        except Exception as inst:
            message = f"Error: {traceback.format_exc()}"

        self.write(message)