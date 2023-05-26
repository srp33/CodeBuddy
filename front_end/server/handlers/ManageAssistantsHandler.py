from BaseUserHandler import *

class ManageAssistantsHandler(BaseUserHandler):
    def get(self, course_id):
        try:
            if self.is_administrator or self.is_instructor_for_course(course_id) or self.is_assistant_for_course(course_id):
                self.render("manage_assistants.html", course_basics=self.get_course_basics(course_id), assistants=self.content.get_users_from_role(course_id, "assistant"), user_info=self.user_info, is_administrator=self.is_administrator, is_assistant=self.is_assistant_for_course(course_id))
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())