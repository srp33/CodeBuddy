import sys
sys.path.append("..")
from ..helper import *
from ..content import *
import traceback
from app.handlers.BaseUserHandler import *
class DeleteExerciseHandler(BaseUserHandler):
    def post(self, course, assignment, exercise):
        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                self.render("permissions.html")
                return

            content.delete_exercise(content.get_exercise_basics(course, assignment, exercise))
        except Exception as inst:
            render_error(self, traceback.format_exc())

