from BaseUserHandler import *

class CoursesHandler(BaseUserHandler):
    def get(self):
        try:
            # First, we check whether this is the first time the app
            # is being accessed. If so, make this user an admin.
            user_count = self.get_content_cookie("user_count", 30)
            if user_count:
                user_count = int(user_count)
            else:
                user_count = self.set_content_cookie("user_count", self.content.get_user_count(), 30)

            if user_count == 1 and not self.content.administrator_exists():
                self.content.add_admin_permissions(self.get_current_user())
                self.redirect(f"/courses")

            if len(self.courses) == 0 and self.is_administrator:
                self.redirect(f"/edit_course/")
            else:
                self.render("courses.html", registered_courses=self.courses, user_info=self.user_info, is_administrator=self.is_administrator)
        except Exception as inst:
            render_error(self, traceback.format_exc())