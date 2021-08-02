from ..helper import *
from ..content import *
import traceback
from BaseUserHandler import *
class ProfileStudentHelpRequestsHandler(BaseUserHandler):
    def get(self):
        try:
            self.render("profile_student_help_requests.html", page="help_requests", result=None, user_info=self.get_user_info(), registered_courses=content.get_registered_courses(self.get_user_id()), help_requests=content.get_student_help_requests(self.get_user_id()), is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
        except Exception as inst:
            render_error(self, traceback.format_exc())

