from BaseUserHandler import *
import datetime as dt

class SubmitHelpRequestHandler(BaseUserHandler):
    def post(self, course_id, assignment_id, exercise_id):
        try:
            user_id = self.get_current_user()
            student_comment = self.get_body_argument("student_comment")
            help_request = self.content.get_help_request(course_id, assignment_id, exercise_id, user_id)
            if help_request:
                self.content.update_help_request(course_id, assignment_id, exercise_id, user_id, student_comment)

            else:
                code = self.get_body_argument("user_code").replace("\r", "")

                course_basics = self.get_course_basics(course_id)
                assignment_basics = self.get_assignment_basics(course_basics, assignment_id)

                # exercise_basics = self.get_exercise_basics(course_basics, assignment_basics, exercise)
                exercise_details = self.get_exercise_details(course_basics, assignment_basics, exercise_id)

                text_output, jpg_output, tests = exec_code(self.settings_dict, code, exercise_details, request=None)
                text_output = format_output_as_html(text_output)

                self.content.save_help_request(course_id, assignment_id, exercise_id, user_id, code, text_output, jpg_output, student_comment, dt.datetime.utcnow())

        except Exception as inst:
            render_error(self, traceback.format_exc())