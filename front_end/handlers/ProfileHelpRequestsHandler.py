from BaseUserHandler import *

class ProfileHelpRequestsHandler(BaseUserHandler):
    def get(self):
        try:
            courses = self.get_courses()

            if self.is_administrator() or self.is_instructor() or self.is_assistant():
                self.render("profile_help_requests.html", page="help_requests", result=None, courses=courses, user_info=user_info, is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

