from BaseUserHandler import *

class CoursesHandler(BaseUserHandler):
    def get(self, new):
        try:
            # First, we check whether this is the first time the app
            # is being accessed. If so, make this user an admin.
            user_count = self.get_content_cookie("user_count", 30)
            if user_count:
                user_count = int(user_count)
            else:
                user_count = self.set_content_cookie("user_count", self.content.get_user_count(), 30)

            if user_count <= 1 and not self.content.administrator_exists():
                self.content.add_admin_permissions(self.get_current_user())
                self.redirect(f"/courses")

            is_admin = self.is_administrator
            registered_courses = self.courses

            if (new == "/new" or len(registered_courses) == 0) and not is_admin:
                registered_course_ids = [x[0] for x in registered_courses]

                available_courses = [course for course in self.content.get_all_courses() if course[0] not in registered_course_ids]

                self.render("register.html", available_courses=available_courses, user_info=self.user_info, is_administrator=is_admin)
            else:
                self.render("courses.html", registered_courses=registered_courses, user_info=self.user_info, is_administrator=is_admin)
        except Exception as inst:
            render_error(self, traceback.format_exc())