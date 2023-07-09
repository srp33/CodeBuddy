from BaseUserHandler import *

class ManageUsersHandler(BaseUserHandler):
    async def get(self):
        try:
            if self.is_administrator:
                self.render("manage_users.html", user_info=self.user_info, is_administrator=self.is_administrator)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def post(self):
        result = {"message": "", "users": []}

        try:
            pattern = self.request.body.decode()

            result["users"] = self.content.get_users_to_manage(f"%{pattern}%")
        except Exception as inst:
            result["message"] = traceback.format_exc()

        self.write(json.dumps(result, default=str))