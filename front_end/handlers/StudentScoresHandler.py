import sys
sys.path.append("..")
from StaticFileHandler import *
from helper import *
import traceback
from BaseUserHandler import *
from content import *

settings_dict = load_yaml_dict(read_file("/Settings.yaml"))
content = Content(settings_dict)

class StudentScoresHandler(BaseUserHandler):
    def get(self, course, assignment, student_id):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                self.render("student_scores.html", student_info=content.get_user_info(student_id), courses=content.get_courses(), course_basics=content.get_course_basics(course), assignments=content.get_assignments(course), assignment_basics=content.get_assignment_basics(course, assignment), exercises=content.get_exercises(course, assignment), exercise_statuses=content.get_exercise_statuses(course, assignment, student_id), user_info=self.get_user_info())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

