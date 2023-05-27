from BaseUserHandler import *

class DeleteHelpRequestHandler(BaseUserHandler):
    def post(self, course_id, assignment_id, exercise_id, user_id):
        try:
            course_basics = self.get_course_basics(course_id)

            self.content.delete_help_request(course_id, assignment_id, exercise_id, user_id)
            self.render("help_requests.html", courses=self.courses, course_basics=course_basics, assignments=self.content.get_assignments(course_basics), help_requests=self.content.get_help_requests(course_id), user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=self.is_instructor_for_course(course_id), is_assistant=self.is_assistant_for_course(course_id))
        except Exception as inst:
            render_error(self, traceback.format_exc())

