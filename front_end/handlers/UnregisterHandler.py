from BaseUserHandler import *

class UnregisterHandler(BaseUserHandler):
    def post(self, course, user_id):
        try:
            if (self.is_student_for_course(course) and self.get_user_id() == user_id) or self.is_administrator() or self.is_instructor_for_course(course):
                if self.content.check_user_registered(course, user_id):
                    self.content.unregister_user_from_course(course, user_id)
                    title = self.content.get_course_basics(course)["title"]
                    result = f"Success: The user {user_id} has been removed from {title}"
                else:
                    result = f"Error: The user {user_id} is not currently registered for the course \"{title}\""

                if self.is_administrator() or self.is_instructor_for_course(course):
                    self.render("profile_instructor.html", page="instructor", tab="manage_students", course=self.content.get_course_basics(course), assignments=self.content.get_assignments(course), instructors=self.content.get_users_from_role(course, "instructor"), assistants=self.content.get_users_from_role(course, "assistant"), registered_students=self.content.get_registered_students(course), result=result, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course))
            else:
                self.render("permissions.html", user_info=self.content.get_user_info(self.get_user_id()), user_logged_in=user_logged_in_var.get())

        except Exception as inst:
            render_error(self, traceback.format_exc())

