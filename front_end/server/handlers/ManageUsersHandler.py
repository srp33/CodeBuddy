from BaseUserHandler import *

class ManageUsersHandler(BaseUserHandler):
    def get(self):
        try:
            if self.is_administrator:
                self.render("manage_users.html", result=None, user_info=self.user_info, is_administrator=self.is_administrator)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self):
        try:
            remove_user = self.get_body_argument("remove_user")
            delete_user = self.get_body_argument("delete_user")

            if remove_user:
                if self.content.user_exists(remove_user):
                    submissions_removed = self.content.remove_user_submissions(remove_user)
                    if submissions_removed:
                        result = f"Success: All scores and submissions for the user '{remove_user}' have been deleted."
                    else:
                        result = f"Error: The user '{remove_user}' doesn't have any submissions to remove."
                else:
                    result = f"Error: The user '{remove_user}' does not exist."
            else:
                result = f"Error: Please enter a user."

            if delete_user:
                course_id = self.content.get_course_id_from_role(delete_user)

                if self.content.user_exists(delete_user):
                    if self.content.is_administrator(delete_user):
                        if len(self.content.get_users_from_role(0, "administrator")) > 1:
                            if delete_user == self.get_current_user():
                                #Figure out what to do when admins remove themselves
                                self.content.delete_user(delete_user)
                            else:
                                result = f"{delete_user} is an administrator and can only be deleted by that user."
                        else:
                            result = f"Error: At least one administrator must remain in the system."
                    elif self.content.user_has_role(delete_user, course_id, "instructor"):
                        if len(self.content.get_users_from_role(course_id, "instructor")) > 1:
                            if self.content.is_administrator(self.get_current_user()):
                                self.content.delete_user(delete_user)
                                result = f"Success: The user '{delete_user}' has been deleted."
                            else:
                                result = "Instructors can only be removed by administrators."
                        else:
                            result = f"Error: The user '{delete_user}' is the only instructor for their course. They cannot be deleted until another instructor is assigned to the course."
                    else:
                        self.content.delete_user(delete_user)
                        result = f"Success: The user '{delete_user}' has been deleted."
                else:
                    result = f"Error: The user '{delete_user}' does not exist."
            else:
                if not remove_user:
                    result = f"Error: Please enter a user."

            self.render("manage_users.html", result=result, user_info=self.user_info, is_administrator=self.is_administrator)
        except Exception as inst:
            render_error(self, traceback.format_exc())