from app.helper import *
from app.content import *
import traceback
from app.handlers.BaseUserHandler import *
import datetime
class ViewAnswerHandler(BaseUserHandler):
    def get(self, course, assignment, exercise):
        try:
            assignment_details = content.get_assignment_details(course, assignment, True)
            client_ip = get_client_ip_address(self.request)
            user = self.get_user_id()
            user_info = self.get_user_info()
            exercise_details = content.get_exercise_details(course, assignment, exercise, format_content=True)
            back_end = settings_dict["back_ends"][exercise_details["back_end"]]

            if assignment_details["allowed_ip_addresses"] and client_ip not in assignment_details[
                "allowed_ip_addresses"] and not self.is_administrator() and not self.is_instructor_for_course(course) and not self.is_assistant_for_course(course):
                self.render("unavailable_assignment.html", courses=content.get_courses(),
                            assignments=content.get_assignments(course),
                            course_basics=content.get_course_basics(course),
                            assignment_basics=content.get_assignment_basics(course, assignment), error="restricted_ip",
                            user_info=user_info)
            else:
                self.render("view_answer.html", courses=content.get_courses(), assignments=content.get_assignments(course), exercises=content.get_exercises(course, assignment), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), assignment_details=content.get_assignment_details(course, assignment), exercise_basics=content.get_exercise_basics(course, assignment, exercise), exercise_details=exercise_details, exercise_statuses=content.get_exercise_statuses(course, assignment, user), code_completion_path=back_end["code_completion_path"], last_submission=content.get_last_submission(course, assignment, exercise, user), student_submissions=content.get_student_submissions(course, assignment, exercise, user), curr_time=datetime.datetime.now(), format_content=True, user_info=self.get_user_info())
        except Exception as inst:
            render_error(self, traceback.format_exc())

