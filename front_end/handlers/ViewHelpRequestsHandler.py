from BaseUserHandler import *

class ViewHelpRequestsHandler(BaseUserHandler):
    def get(self, course, assignment, exercise, student_id):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                self.render("view_request.html", courses=self.content.get_courses(), course_basics=self.content.get_course_basics(course), assignments=self.content.get_assignments(course), assignment_basics=self.content.get_assignment_basics(course, assignment), exercises=self.content.get_exercises(course, assignment), exercise_basics=self.content.get_exercise_basics(course, assignment, exercise), exercise_details=self.content.get_exercise_details(course, assignment, exercise), help_request=self.content.get_help_request(course, assignment, exercise, student_id), exercise_help_requests=self.content.get_exercise_help_requests(course, assignment, exercise, student_id), similar_requests=self.content.compare_help_requests(course, assignment, exercise, student_id), result=None, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course))
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post (self, course, assignment, exercise, student_id):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                suggestion = self.get_body_argument("suggestion")
                more_info_needed = self.get_argument("more_info_needed", None) == "More info needed"
                user_id = self.get_user_id()
                if self.is_assistant_for_course(course):
                    self.content.save_help_request_suggestion(course, assignment, exercise, student_id, suggestion, 0, user_id, None, more_info_needed)
                    result = "Success: suggestion submitted for approval"
                else:
                    help_request = self.content.get_help_request(course, assignment, exercise, student_id)
                    if help_request["suggester_id"]:
                        suggester_id = help_request["suggester_id"]
                    else:
                        suggester_id = user_id
                    self.content.save_help_request_suggestion(course, assignment, exercise, student_id, suggestion, 1, suggester_id, user_id, more_info_needed)
                    result = "Success: suggestion saved"

                self.render("view_request.html", courses=self.content.get_courses(), course_basics=self.content.get_course_basics(course), assignments=self.content.get_assignments(course), assignment_basics=self.content.get_assignment_basics(course, assignment), exercises=self.content.get_exercises(course, assignment), exercise_basics=self.content.get_exercise_basics(course, assignment, exercise), exercise_details=self.content.get_exercise_details(course, assignment, exercise), help_request=self.content.get_help_request(course, assignment, exercise, student_id), exercise_help_requests=self.content.get_exercise_help_requests(course, assignment, exercise, student_id), similar_requests=self.content.compare_help_requests(course, assignment, exercise, student_id), result=result, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course))
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

