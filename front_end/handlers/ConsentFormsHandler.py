from .helper import *
from .content import *
import traceback
from BaseUserHandler import *
class ConsentFormsHandler(BaseUserHandler):
    def get(self, user_id):
        try:
            if self.is_administrator():
                registered_courses = content.get_courses()

                # Adds a list of students to each course.
                for course in registered_courses:
                    course[1].update({"student_names": content.get_registered_students(course[0])})
            elif self.is_instructor():
                registered_courses = content.get_courses_connected_to_user(user_id)


                # Adds a list of students to each course.
                for course in registered_courses:
                    course[1].update({"student_names": content.get_registered_students(course[0])})
            else:
                registered_courses = content.get_registered_courses(user_id)

            self.render("consent_forms.html", page="consent_forms", result=None, registered_courses=registered_courses, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
        except Exception as inst:
            render_error(self, traceback.format_exc())

