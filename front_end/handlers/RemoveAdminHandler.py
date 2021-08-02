import sys
sys.path.append("..")
from ..helper import *
from ..content import *
import traceback
from BaseUserHandler import *
class RemoveAdminHandler(BaseUserHandler):
    def post(self, user_id):
        try:
            if not self.is_administrator():
                self.render("permissions.html")
                return

            content.remove_permissions(None, user_id, "administrator")
            self.render("profile_courses.html", page="courses", result=None, courses=content.get_courses(), registered_courses=content.get_registered_courses(user_id), user_info=self.get_user_info(), is_administrator=False, is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
        except Exception as inst:
            render_error(self, traceback.format_exc())

