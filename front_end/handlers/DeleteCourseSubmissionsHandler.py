from BaseUserHandler import *


class DeleteCourseSubmissionsHandler(BaseUserHandler):
    def post(self, course):
        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                self.render("permissions.html")
                return

            self.content.delete_course_submissions(self.content.get_course_basics(course))
        except Exception as inst:
            render_error(self, traceback.format_exc())

