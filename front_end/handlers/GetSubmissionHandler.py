import sys
sys.path.append("..")
from content import *
import traceback
from app.handlers.BaseUserHandler import *
class GetSubmissionHandler(BaseUserHandler):
    def get(self, course, assignment, exercise, student_id, submission_id):
        try:
            assignment_details = content.get_assignment_details(course, assignment, True)
            client_ip = get_client_ip_address(self.request)
            user_info = self.get_user_info()

            if assignment_details["allowed_ip_addresses"] and client_ip not in assignment_details[
               "allowed_ip_addresses"] and not self.is_administrator() and not self.is_instructor_for_course(course) and not self.is_assistant_for_course(course):
               self.render("unavailable_assignment.html", courses=content.get_courses(),
                           assignments=content.get_assignments(course),
                           course_basics=content.get_course_basics(course),
                           assignment_basics=content.get_assignment_basics(course, assignment), error="restricted_ip",
                           user_info=user_info)
            elif user_info["user_id"] != student_id and not self.is_administrator() and not self.is_instructor_for_course(course) and not self.is_assistant_for_course(course):
                submission_info = ["Submissions may only be view by their author."]
            else:
                exercise_details = content.get_exercise_details(course, assignment, exercise)
                submission_info = content.get_submission_info(course, assignment, exercise, student_id, submission_id)

                diff, passed, tests = check_exercise_output(exercise_details, submission_info["text_output"], submission_info["image_output"], submission_info["tests"])

                submission_info["diff"] = format_output_as_html(diff)
                submission_info["text_output"] = submission_info["text_output"]
                submission_info["tests"] = tests
        except Exception as inst:
            submission_info["diff"] = ""
            submission_info["text_output"] = format_output_as_html(traceback.format_exc())

        self.write(json.dumps(submission_info))

