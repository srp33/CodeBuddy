import sys
sys.path.append("..")
from helper import *
import traceback
from BaseUserHandler import *
from content import *

settings_dict = load_yaml_dict(read_file("/Settings.yaml"))
content = Content(settings_dict)

class ProfileHelpRequestsHandler(BaseUserHandler):
    def get(self):
        try:
            if self.is_administrator() or self.is_instructor() or self.is_assistant():
                user_info=self.get_user_info()
                if self.is_administrator():
                    courses = content.get_courses()
                elif self.is_instructor() or self.is_assistant():
                    courses = content.get_courses_connected_to_user(user_info["user_id"])

                self.render("profile_help_requests.html", page="help_requests", result=None, courses=courses, user_info=user_info, is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

