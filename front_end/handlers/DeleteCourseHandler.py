from BaseUserHandler import *

class DeleteCourseHandler(BaseUserHandler):
    def get(self, course):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course):
                self.render("delete_course.html", courses=self.get_courses(), course_basics=self.content.get_course_basics(course), result=None, user_info=self.get_user_info())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course):
        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                self.render("permissions.html")
                return

            self.content.delete_course(self.content.get_course_basics(course))
            result = "Success: Course deleted."

            self.render("delete_course.html", courses=self.get_courses(), course_basics=self.content.get_course_basics(None), result=result, user_info=self.get_user_info())
        except Exception as inst:
            render_error(self, traceback.format_exc())

