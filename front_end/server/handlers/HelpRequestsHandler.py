from BaseUserHandler import *

class HelpRequestsHandler(BaseUserHandler):
    def get(self, course_id):
        try:
            if self.is_administrator or self.is_instructor_for_course(course_id) or self.is_assistant_for_course(course_id):
                course_basics = self.get_course_basics(course_id)

                self.render("help_requests.html", courses=self.courses, course_basics=course_basics, assignments=self.get_assignments(course_basics), help_requests=self.content.get_help_requests(course_id), user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=self.is_instructor_for_course(course_id), is_assistant=self.is_assistant_for_course(course_id))
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())