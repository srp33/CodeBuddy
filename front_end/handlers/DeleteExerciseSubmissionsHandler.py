import sys
sys.path.append("..")
from StaticFileHandler import *
from helper import *
import traceback
from BaseUserHandler import *
from content import *

settings_dict = load_yaml_dict(read_file("/Settings.yaml"))
content = Content(settings_dict)

class DeleteExerciseSubmissionsHandler(BaseUserHandler):
    def post(self, course, assignment, exercise):
        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                self.render("permissions.html")
                return

            content.delete_exercise_submissions(content.get_exercise_basics(course, assignment, exercise))
        except Exception as inst:
            render_error(self, traceback.format_exc())

