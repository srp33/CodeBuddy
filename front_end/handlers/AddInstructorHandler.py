import traceback
from BaseUserHandler import *


class AddInstructorHandler(BaseUserHandler):
    def get(self, course):
        try:
            if self.is_administrator():
                course_basics = content.get_course_basics(course)
                self.render("add_instructor.html", courses=content.get_courses(), course_basics=course_basics, instructors=content.get_users_from_role(course_basics["id"], "instructor"), result=None, user_info=self.get_user_info())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course):
        try:
            if not self.is_administrator():
                self.render("permissions.html")
                return

            course_basics = content.get_course_basics(course)
            new_instructor = self.get_body_argument("new_inst")

            if content.user_exists(new_instructor):
                if content.is_administrator(new_instructor):
                    result = f"Error: {new_instructor} is already an administrator and can't be given a lower role."
                else:
                    content.add_permissions(course_basics["id"], new_instructor, "instructor")
                    result = f"Success! {new_instructor} is now an instructor for the {course_basics['title']} course."
            else:
                result = f"Error: The user '{new_instructor}' does not exist."

            self.render("add_instructor.html", courses=content.get_courses(), course_basics=course_basics, instructors=content.get_users_from_role(course_basics["id"], "instructor"), result=result, user_info=self.get_user_info())
        except Exception as inst:
            render_error(self, traceback.format_exc())

