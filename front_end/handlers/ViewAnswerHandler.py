from BaseUserHandler import *
import datetime as dt

class ViewAnswerHandler(BaseUserHandler):
    def get(self, course, assignment, exercise):
        try:
            assignment_details = self.content.get_assignment_details(course, assignment, True)
            client_ip = get_client_ip_address(self.request)
            user = self.get_user_id()
            user_info = self.get_user_info()
            exercise_details = self.content.get_exercise_details(course, assignment, exercise, format_content=True)
            back_end = self.settings_dict["back_ends"][exercise_details["back_end"]]

            if assignment_details["allowed_ip_addresses"] and client_ip not in assignment_details[
                "allowed_ip_addresses"] and not self.is_administrator() and not self.is_instructor_for_course(course) and not self.is_assistant_for_course(course):
                self.render("unavailable_assignment.html", courses=self.content.get_courses(),
                            assignments=self.content.get_assignments(course),
                            course_basics=self.content.get_course_basics(course),
                            assignment_basics=self.content.get_assignment_basics(course, assignment), error="restricted_ip",
                            user_info=user_info)
            else:
                self.render("view_answer.html", courses=self.content.get_courses(), assignments=self.content.get_assignments(course), exercises=self.content.get_exercises(course, assignment), course_basics=self.content.get_course_basics(course), assignment_basics=self.content.get_assignment_basics(course, assignment), assignment_details=self.content.get_assignment_details(course, assignment), exercise_basics=self.content.get_exercise_basics(course, assignment, exercise), exercise_details=exercise_details, exercise_statuses=self.content.get_exercise_statuses(course, assignment, user), code_completion_path=back_end["code_completion_path"], last_submission=self.content.get_last_submission(course, assignment, exercise, user), peer_submissions=self.content.get_peer_submissions(course, assignment, exercise, user), curr_time=dt.datetime.now(), format_content=True, user_info=self.get_user_info())
        except Exception as inst:
            render_error(self, traceback.format_exc())

