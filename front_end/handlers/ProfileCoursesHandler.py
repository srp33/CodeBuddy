from StaticFileHandler import *
from helper import *
import traceback
from BaseUserHandler import *
from content import *


settings_dict = load_yaml_dict(read_file("/Settings.yaml"))
content = Content(settings_dict)

class ProfileCoursesHandler(BaseUserHandler):
    def get(self, user_id):
        try:
            if self.is_administrator():
                registered_courses = content.get_courses()
                available_courses = None
            elif self.is_instructor() or self.is_assistant():
                registered_courses = content.get_courses_connected_to_user(user_id)
                available_courses = None
            else:
                registered_courses = content.get_registered_courses(user_id)
                available_courses = content.get_available_courses(user_id)

            self.render("profile_courses.html", page="courses", result=None, available_courses=available_courses, registered_courses=registered_courses, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, user_id):
        try:
            course_id = self.get_body_argument("course_id")
            passcode = self.get_body_argument("passcode")
            consent_given = self.get_body_argument("consent_given") == "Yes"

            course_basics = content.get_course_basics(course_id)
            course_details = content.get_course_details(course_id)
            course_title = course_basics["title"]
            course_passcode = course_details["passcode"]
            result = ""

            if not consent_given:
                result = "You may not register for this course without providing consent to participate in the research study. Please review the instructions on what you should do if you decline to participate in the study."
            elif (course_passcode == None or course_passcode == passcode):
                if (content.course_exists(course_id)):
                    if (content.check_user_registered(course_id, user_id)):
                        result = f"Error: You are already registered for {course_title}."
                    else:
                        content.register_user_for_course(course_id, user_id)
                        result = f"Success: You're now registered for {course_title}."
                else:
                    result = "Error: A course with that ID was not found."
            elif passcode == "":
                result = "Error: Please enter a passcode."
            else:
                result = "Error: Incorrect passcode."

            if self.is_administrator():
                registered_courses = content.get_courses()
                available_courses = None
            elif self.is_instructor() or self.is_assistant():
                registered_courses = content.get_courses_connected_to_user(user_id)
                available_courses = None
            else:
                registered_courses = content.get_registered_courses(user_id)
                available_courses = content.get_available_courses(user_id)

            self.render("profile_courses.html", page="courses", result=result, available_courses=available_courses, registered_courses=registered_courses, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
        except Exception as inst:
            render_error(self, traceback.format_exc())

