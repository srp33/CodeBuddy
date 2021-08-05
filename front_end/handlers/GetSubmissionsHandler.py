from BaseUserHandler import *
from content import *


class GetSubmissionsHandler(BaseUserHandler):
    def get(self, course, assignment, exercise, user_id):
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
            elif user_info["user_id"] != user_id and not self.is_administrator() and not self.is_instructor_for_course(course) and not self.is_assistant_for_course(course):
                submission_info = ["Submissions may only be view by their author."]
            else:
                submissions = content.get_submissions_basic(course, assignment, exercise, user_id)
        except Exception as inst:
            submissions = []

        self.write(json.dumps(submissions))

