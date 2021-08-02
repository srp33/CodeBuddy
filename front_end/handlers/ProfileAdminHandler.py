import sys
sys.path.append("..")
from app.helper import *
from app.content import *
import traceback
from app.handlers.BaseUserHandler import *
class ProfileAdminHandler(BaseUserHandler):
    def get (self, user_id):
        try:
            if self.is_administrator():
                self.render("profile_admin.html", page="admin", tab=None, registered_courses=content.get_registered_courses(user_id), admins=content.get_users_from_role(0, "administrator"), result=None, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, user_id):
        try:
            if not self.is_administrator():
                self.render("permissions.html")
                return

            new_admin = self.get_body_argument("new_admin")

            if content.user_exists(new_admin):
                if content.is_administrator(new_admin):
                    result = f"{new_admin} is already an administrator."
                else:
                    content.add_admin_permissions(new_admin)
                    result = f"Success! {new_admin} is an administrator."
            else:
                result = f"Error: The user '{new_admin}' does not exist."

            self.render("profile_admin.html", page="admin", tab="manage", admins=content.get_users_from_role(0, "administrator"), result=result, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
        except Exception as inst:
            render_error(self, traceback.format_exc())

