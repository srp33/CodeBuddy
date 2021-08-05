import sys
sys.path.append("..")
from helper import *
import traceback
from BaseUserHandler import *
import datetime
from content import *

settings_dict = load_yaml_dict(read_file("/Settings.yaml"))
content = Content(settings_dict)

class EditCourseHandler(BaseUserHandler):
    def get(self, course):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course):
                self.render("edit_course.html", courses=content.get_courses(), assignments=content.get_assignments(course), course_basics=content.get_course_basics(course), course_details=content.get_course_details(course), result=None, user_info=self.get_user_info())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course):
        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                self.render("permissions.html")
                return

            course_basics = content.get_course_basics(course)
            course_details = content.get_course_details(course)

            course_basics["title"] = self.get_body_argument("title").strip()
            course_basics["visible"] = self.get_body_argument("is_visible") == "Yes"
            course_details["introduction"] = self.get_body_argument("introduction").strip()
            course_details["passcode"] = self.get_body_argument("passcode").strip()
            course_details["consent_text"] = self.get_body_argument("consent_form").strip()
            course_details["consent_alternative_text"] = self.get_body_argument("consent_alternative").strip()
            course_details["enable_research"] = self.get_body_argument("enable_research") == "Yes"

            if course_details["passcode"] == "":
                course_details["passcode"] = None

            result = "Success: Course information saved!"

            if course_basics["title"] == "" or course_details["introduction"] == "":
                result = "Error: Missing title or introduction."
            elif course_details["enable_research"] and (course_details["consent_text"] == "" or course_details["consent_alternative_text"] == ""):
                result = "Error: Missing consent form or consent alternative form."
            else:
                if content.has_duplicate_title(content.get_courses(), course_basics["id"], course_basics["title"]):
                    result = "Error: A course with that title already exists."
                else:
                    #if re.search(r"[^\w ]", title):
                    #    result = "Error: The title can only contain alphanumeric characters and spaces."
                    #else:
                    if len(course_basics["title"]) > 80:
                        result = "Error: The title cannot exceed 80 characters."
                    else:
                        #content.specify_course_basics(course_basics, course_basics["title"], course_basics["visible"])
                        content.specify_course_details(course_details, course_details["introduction"], course_details["passcode"], course_details["consent_text"], course_details["consent_alternative_text"], None, datetime.datetime.now())
                        course = content.save_course(course_basics, course_details)

            self.render("edit_course.html", courses=content.get_courses(), assignments=content.get_assignments(course), course_basics=course_basics, course_details=course_details, result=result, user_info=self.get_user_info())
        except Exception as inst:
            render_error(self, traceback.format_exc())

