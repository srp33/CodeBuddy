from BaseUserHandler import *

class RemoveAssistantHandler(BaseUserHandler):
    def get(self, course_id, user_id):
        message = "Error: You do not have permission to perform that task."

        try:
            if self.is_administrator or self.is_instructor_for_course(course_id) or user_id == self.get_current_user():
                if self.content.user_has_role(user_id, course_id, "assistant"):
                    self.content.remove_permissions(course_id, user_id, "assistant")

                message = "Success"
        except Exception as inst:
            message = f"Error: {traceback.format_exc()}"

        self.write(message)