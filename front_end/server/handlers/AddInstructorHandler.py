from BaseUserHandler import *

class AddInstructorHandler(BaseUserHandler):
    def get(self, course_id, user_id):
        message = "Error: You do not have permission to perform that task."

        try:
            if self.is_administrator or self.is_instructor_for_course(course_id):
                if self.content.user_exists(user_id):
                    if self.content.is_administrator(user_id):
                        message = f"Error: The user '{user_id}' is already an administrator."
                    elif self.content.user_has_role(user_id, course_id, "instructor"):
                        message = f"Error: The user '{user_id}' is already an instructor."
                    elif self.content.user_has_role(user_id, course_id, "assistant"):
                        message = f"Error: The user '{user_id}' is already an assistant."
                    else:
                        self.content.add_permissions(course_id, user_id, "instructor")
                        message = "Success"
                else:
                    message = f"Error: The user '{user_id}' does not exist."
        except Exception as inst:
            message = f"Error: {traceback.format_exc()}"

        self.write(message)