from BaseUserHandler import *

class MyProfileHandler(BaseUserHandler):
    async def get(self, user_id):
        try:
            self.render("my_profile.html", user_info=self.user_info, is_administrator=self.is_administrator)
        except Exception as inst:
            render_error(self, traceback.format_exc())