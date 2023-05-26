from BaseUserHandler import *

class UnregisterHandler(BaseUserHandler):
    def get(self, course, user_id):
        result = "Error: No response"

        try:
            if self.get_current_user() == user_id or self.is_administrator or self.is_instructor_for_course(course):

                title = self.get_course_basics(course)["title"]
                if self.content.is_user_registered(course, user_id):
                    self.content.unregister_user_from_course(course, user_id)
                    #TODO: Clear cookie for courses

                    result = f"Success: The user {user_id} has been removed from {title}"
                else:
                    result = f"Error: The user {user_id} is not currently registered for the course \"{title}\""
            else:
                result = f"Error: You do not have permissions to perform this task."
        except Exception as inst:
            result = f"Error: {traceback.format_exc()}"

        self.write(result)