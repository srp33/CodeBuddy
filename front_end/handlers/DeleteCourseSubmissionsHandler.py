import sys
sys.path.append("..")
from app.helper import *
from app.content import *
import traceback
from app.handlers.BaseUserHandler import *
class DeleteCourseSubmissionsHandler(BaseUserHandler):
    def post(self, course):
        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                self.render("permissions.html")
                return

            content.delete_course_submissions(content.get_course_basics(course))
        except Exception as inst:
            render_error(self, traceback.format_exc())

