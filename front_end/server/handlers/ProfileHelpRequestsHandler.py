from BaseUserHandler import *

class ProfileHelpRequestsHandler(BaseUserHandler):
    def get(self):
        try:
            if self.is_administrator:
                self.render("profile_help_requests.html", page="help_requests", result=None, courses=self.courses, user_info=user_info, is_administrator=self.is_administrator)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())