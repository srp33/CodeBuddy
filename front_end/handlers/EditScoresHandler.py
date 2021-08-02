import sys
sys.path.append("..")
from app.helper import *
from app.content import *
import traceback
from app.handlers.BaseUserHandler import *
class EditScoresHandler(BaseUserHandler):
    def get(self, course, assignment, student_id):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                self.render("edit_scores.html", student_id=student_id, courses=content.get_courses(), course_basics=content.get_course_basics(course), assignments=content.get_assignments(course), assignment_basics=content.get_assignment_basics(course, assignment), exercises=content.get_exercises(course, assignment), exercise_statuses=content.get_exercise_statuses(course, assignment, student_id), result=None, user_info=self.get_user_info())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course, assignment, student_id):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):

                exercise_statuses = content.get_exercise_statuses(course, assignment, student_id)
                result = ""
                for exercise in exercise_statuses:
                    student_score = self.get_body_argument(str(exercise[1]["id"]))
                    if (student_score.isnumeric()):
                        result = f"Success: {student_id}'s scores for this assignment have been updated."
                        content.save_exercise_score(course, assignment, exercise[1]["id"], student_id, int(student_score))
                    else:
                        result = "Error: Newly entered scores must be numeric."

                self.render("edit_scores.html", student_id=student_id, courses=content.get_courses(), course_basics=content.get_course_basics(course), assignments=content.get_assignments(course), assignment_basics=content.get_assignment_basics(course, assignment), exercises=content.get_exercises(course, assignment), exercise_statuses=content.get_exercise_statuses(course, assignment, student_id), result=result, user_info=self.get_user_info())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

