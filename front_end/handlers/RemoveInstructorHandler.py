from BaseUserHandler import *

class RemoveInstructorHandler(BaseUserHandler):
    def post(self, course, old_instructor):
        try:
            if not self.is_administrator():
                self.render("permissions.html")
                return

            if not self.content.user_has_role(old_instructor, course, "instructor"):
                result = f"Error: {old_instructor} is not an instructor for this course."
            else:
                self.content.remove_permissions(course, old_instructor, "instructor")
                result = f"Success: {old_instructor} has been removed from the instructor list."

            self.render("profile_instructor.html", page="instructor", tab="manage_instructors", course=self.content.get_course_basics(course), assignments=self.content.get_assignments(course), instructors=self.content.get_users_from_role(course, "instructor"), assistants=self.content.get_users_from_role(course, "assistant"), registered_students=self.content.get_registered_students(course), result=result, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course))
        except Exception as inst:
            render_error(self, traceback.format_exc())

