import sys
sys.path.append("..")
from app.helper.helper import *
from app.content.content import *
import traceback
from app.handlers.BaseUserHandler import *
class DeleteCourseHandler(BaseUserHandler):
    def get(self, course):
        try:
            if self.is_administrator():
                self.render("delete_course.html", courses=content.get_courses(), course_basics=content.get_course_basics(course), result=None, user_info=self.get_user_info())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course):
        try:
            if not self.is_administrator():
                self.render("permissions.html")
                return

            content.delete_course(content.get_course_basics(course))
            result = "Success: Course deleted."

            self.render("delete_course.html", courses=content.get_courses(), course_basics=content.get_course_basics(None), result=result, user_info=self.get_user_info())
        except Exception as inst:
            render_error(self, traceback.format_exc())

