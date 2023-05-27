from BaseUserHandler import *

class PersonalInfoHandler(BaseUserHandler):
    def get(self, user_id):
        try:
            self.render("personal_info.html", page="personal_info", user_info=self.user_info, is_administrator=self.is_administrator)
        except Exception as inst:
            render_error(self, traceback.format_exc())