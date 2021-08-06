import traceback
from BaseUserHandler import *


class StudentScoresHandler(BaseUserHandler):
    def get(self, course, assignment, student_id):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                self.render("student_scores.html", student_info=self.content.get_user_info(student_id), courses=self.content.get_courses(), course_basics=self.content.get_course_basics(course), assignments=self.content.get_assignments(course), assignment_basics=self.content.get_assignment_basics(course, assignment), exercises=self.content.get_exercises(course, assignment), exercise_statuses=self.content.get_exercise_statuses(course, assignment, student_id), user_info=self.get_user_info())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

