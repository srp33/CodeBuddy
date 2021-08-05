import sys
sys.path.append("..")
from helper import *
import traceback
from BaseUserHandler import *
from content import *
settings_dict = load_yaml_dict(read_file("/Settings.yaml"))
content = Content(settings_dict)


class ProfileManageUsersHandler(BaseUserHandler):
    def get(self):
        try:
            if self.is_administrator() or self.is_instructor():
                self.render("profile_manage_users.html", page="manage_users", result=None, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self):
        try:
            remove_user = self.get_body_argument("remove_user")
            delete_user = self.get_body_argument("delete_user")

            if remove_user:
                if content.user_exists(remove_user):
                    submissions_removed = content.remove_user_submissions(remove_user)
                    if submissions_removed:
                        result = f"Success: All scores and submissions for the user '{remove_user}' have been deleted."
                    else:
                        result = f"Error: The user '{remove_user}' doesn't have any submissions to remove."
                else:
                    result = f"Error: The user '{remove_user}' does not exist."
            else:
                result = f"Error: Please enter a user."

            if delete_user:
                course_id = content.get_course_id_from_role(delete_user)

                if content.user_exists(delete_user):
                    if content.is_administrator(delete_user):
                        if len(content.get_users_from_role(0, "administrator")) > 1:
                            if delete_user == self.get_user_id():
                                #Figure out what to do when admins remove themselves
                                content.delete_user(delete_user)
                            else:
                                result = f"{delete_user} is an administrator and can only be deleted by that user."
                        else:
                            result = f"Error: At least one administrator must remain in the system."
                    elif content.user_has_role(delete_user, course_id, "instructor"):
                        if len(content.get_users_from_role(course_id, "instructor")) > 1:
                            if content.is_administrator(user_id):
                                content.delete_user(delete_user)
                                result = f"Success: The user '{delete_user}' has been deleted."
                            else:
                                result = "Instructors can only be removed by administrators."
                        else:
                            result = f"Error: The user '{delete_user}' is the only instructor for their course. They cannot be deleted until another instructor is assigned to the course."
                    else:
                        content.delete_user(delete_user)
                        result = f"Success: The user '{delete_user}' has been deleted."
                else:
                    result = f"Error: The user '{delete_user}' does not exist."
            else:
                if not remove_user:
                    result = f"Error: Please enter a user."

            self.render("profile_manage_users.html", page="manage_users", result=result, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
        except Exception as inst:
            render_error(self, traceback.format_exc())

