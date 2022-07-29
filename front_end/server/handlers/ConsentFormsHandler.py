from BaseUserHandler import *

class ConsentFormsHandler(BaseUserHandler):
    def get(self, user_id):
        try:
            registered_courses = self.get_courses()

            if self.is_administrator() or self.is_instructor():
                # Adds a list of students to each course.
                for course in registered_courses:
                    course[1].update({"student_names": self.content.get_registered_students(course[0])})

            self.render("consent_forms.html", page="consent_forms", result=None, registered_courses=registered_courses, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
        except Exception as inst:
            render_error(self, traceback.format_exc())

