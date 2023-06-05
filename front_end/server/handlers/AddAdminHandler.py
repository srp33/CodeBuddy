from BaseUserHandler import *

class AddAdminHandler(BaseUserHandler):
    async def get(self, user_id):
        message = "Error: You do not have permission to perform that task."

        try:
            if self.is_administrator:
                if self.content.user_exists(user_id) and not self.content.is_administrator(user_id):
                    self.content.add_admin_permissions(user_id)
                    message = "Success"
                else:
                    result = f"Error: The user '{user_id}' does not exist."
        except Exception as inst:
            message = f"Error: {traceback.format_exc()}"

        self.write(message)