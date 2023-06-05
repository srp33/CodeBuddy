from BaseUserHandler import *

class ManageAdminsHandler(BaseUserHandler):
    async def get(self):
        try:
            if self.is_administrator:
                self.render("manage_admins.html", admins=self.content.get_users_from_role(0, "administrator"), user_info=self.user_info, is_administrator=self.is_administrator)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())