from BaseUserHandler import *

class ProfileInstructorHandler(BaseUserHandler):
    def get (self, course_id, user_id):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course_id):
                self.render("profile_instructor.html", page="instructor", tab=None, course=self.content.get_course_basics(course_id), assignments=self.content.get_assignments(course_id), instructors=self.content.get_users_from_role(course_id, "instructor"), assistants=self.content.get_users_from_role(course_id, "assistant"), registered_students=self.content.get_registered_students(course_id), result=None, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course_id), is_assistant=self.is_assistant_for_course(course_id))
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course_id, user_id):
        try:
            new_assistant = self.get_body_argument("new_assistant")
            new_instructor = self.get_body_argument("new_instructor")
            result = ""
            tab = ""

            if new_assistant:
                tab = "manage_assistants"
                if self.is_administrator() or self.is_instructor_for_course(course_id):
                    if self.content.user_exists(new_assistant):
                        if self.content.user_has_role(new_assistant, course_id, "assistant"):
                            result = f"{new_assistant} is already an assistant for this course."
                        else:
                            self.content.add_permissions(course_id, new_assistant, "assistant")
                            result = f"Success! {new_assistant} is now an assistant for this course."
                    else:
                        result = f"Error: The user '{new_assistant}' does not exist."
                else:
                    self.render("permissions.html")

            elif new_instructor:
                tab = "manage_instructors"
                if self.is_administrator():
                    if self.content.user_exists(new_instructor):
                        if self.content.user_has_role(new_instructor, course_id, "instructor"):
                            result = f"{new_instructor} is already an instructor for this course."
                        else:
                            self.content.add_permissions(course_id, new_instructor, "instructor")
                            result = f"Success! {new_instructor} is now an instructor for this course."
                    else:
                        result = f"Error: The user '{new_instructor}' does not exist."
                else:
                    self.render("permissions.html")

            self.render("profile_instructor.html", page="instructor", tab=tab, course=self.content.get_course_basics(course_id), assignments=self.content.get_assignments(course_id), instructors=self.content.get_users_from_role(course_id, "instructor"), assistants=self.content.get_users_from_role(course_id, "assistant"), registered_students=self.content.get_registered_students(course_id), result=result, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course_id), is_assistant=self.is_assistant_for_course(course_id))
        except Exception as inst:
            render_error(self, traceback.format_exc())

