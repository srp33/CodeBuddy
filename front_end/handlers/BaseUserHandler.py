import sys
sys.path.append("..")
from helper import *
from tornado.web import *
import traceback
from content import *
import contextvars




settings_dict = load_yaml_dict(read_file("/Settings.yaml"))
content = Content(settings_dict)
user_info_var = contextvars.ContextVar("user_info")
contextvars.ContextVar("user_is_administrator")
contextvars.ContextVar("user_instructor_courses")
contextvars.ContextVar("user_assistant_courses")

class BaseUserHandler(RequestHandler):
    def prepare(self):
        try:
            user_id = self.get_secure_cookie("user_id")

            # Set context variables depending on whether the user is logged in.
            if user_id:
                user_info_var.set(content.get_user_info(user_id.decode()))
                user_is_administrator_var.set(content.is_administrator(user_id.decode()))
                user_instructor_courses_var.set([str(x) for x in content.get_courses_with_role(user_id.decode(), "instructor")])
                user_assistant_courses_var.set([str(x) for x in content.get_courses_with_role(user_id.decode(), "assistant")])
            else:
                if settings_dict["mode"] == "production":
                    self.set_secure_cookie("redirect_path", self.request.path)
                    self.redirect("/login")
                else:
                    self.redirect("/devlogin{}".format(self.request.path))
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def get_user_info(self):
        return user_info_var.get()

    def get_user_id(self):
        return self.get_user_info()["user_id"]

    def is_administrator(self):
        return user_is_administrator_var.get()

    def is_instructor(self):
        return len(user_instructor_courses_var.get()) > 0

    def is_assistant(self):
        return len(user_assistant_courses_var.get()) > 0

    def is_instructor_for_course(self, course_id):
        return course_id in user_instructor_courses_var.get()

    def is_assistant_for_course(self, course_id):
        return course_id in user_assistant_courses_var.get()

    def is_student_for_course(self, course_id):
        return not self.is_administrator() and not self.is_instructor_for_course(course_id) and not self.is_assistant_for_course(course_id)

