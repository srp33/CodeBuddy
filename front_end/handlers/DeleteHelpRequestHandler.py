import traceback
from BaseUserHandler import *


class DeleteHelpRequestHandler(BaseUserHandler):
    def post(self, course, assignment, exercise, user_id):
        try:
            content.delete_help_request(course, assignment, exercise, user_id)
            self.render("help_requests.html", courses=content.get_courses(), course_basics=content.get_course_basics(course), assignments=content.get_assignments(course), help_requests=content.get_help_requests(course), user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course))
        except Exception as inst:
            render_error(self, traceback.format_exc())

