from BaseUserHandler import *

class AvailableCoursesHandler(BaseUserHandler):
    def get(self):
        try:
            if self.is_administrator:
                self.redirect(f"/courses")

            registered_course_ids = [x[0] for x in self.courses]

            available_courses = [course for course in self.content.get_all_courses() if course[0] not in registered_course_ids]

            self.render("available.html", available_courses=available_courses, user_info=self.user_info, is_administrator=self.is_administrator)
        except Exception as inst:
            render_error(self, traceback.format_exc())