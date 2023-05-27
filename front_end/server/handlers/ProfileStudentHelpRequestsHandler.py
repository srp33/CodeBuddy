from BaseUserHandler import *

class ProfileStudentHelpRequestsHandler(BaseUserHandler):
    def get(self):
        try:
            self.render("profile_student_help_requests.html", page="help_requests", result=None, user_info=self.user_info, help_requests=self.content.get_student_help_requests(self.get_current_user()), is_administrator=self.is_administrator)
        except Exception as inst:
            render_error(self, traceback.format_exc())