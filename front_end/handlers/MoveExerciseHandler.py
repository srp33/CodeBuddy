import sys
sys.path.append("..")
from helper import *
import traceback
from BaseUserHandler import *
from content import *
settings_dict = load_yaml_dict(read_file("/Settings.yaml"))
content = Content(settings_dict)


class MoveExerciseHandler(BaseUserHandler):
    def post(self, course, assignment, exercise):
        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                self.render("permissions.html")
                return

            new_assignment_id = self.get_body_argument("new_assignment_id")
            content.move_exercise(course, assignment, exercise, new_assignment_id)
            assignment_basics = content.get_assignment_basics(course, assignment)

            out_file = f"Assignment_{new_assignment_id}_Scores.csv"

            self.render("assignment_admin.html", courses=content.get_courses(True), assignments=content.get_assignments(course, True), exercises=content.get_exercises(course, assignment, True), exercise_statuses=content.get_exercise_statuses(course, assignment, self.get_user_info()["user_id"]), course_basics=content.get_course_basics(course), assignment_basics=assignment_basics, assignment_details=content.get_assignment_details(course, assignment, True), download_file_name=get_scores_download_file_name(assignment_basics), course_options=[x[1] for x in content.get_courses() if str(x[0]) != course], user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), out_file=out_file)
        except Exception as inst:
            render_error(self, traceback.format_exc())

