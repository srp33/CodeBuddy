import sys
sys.path.append("..")
from helper import *
import traceback
from BaseUserHandler import *
from content import *

settings_dict = load_yaml_dict(read_file("/Settings.yaml"))
content = Content(settings_dict)

class RemoveAssistantHandler(BaseUserHandler):
    def post(self, course, old_assistant):
        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                self.render("permissions.html")
                return

            if not content.user_has_role(old_assistant, course, "assistant"):
                result = f"Error: {old_assistant} is not an assistant for this course."
            else:
                content.remove_permissions(course, old_assistant, "assistant")
                result = f"Success: {old_assistant} has been removed from the instructor assistant list."

            self.render("profile_instructor.html", page="instructor", tab="manage_assistants", course=content.get_course_basics(course), assignments=content.get_assignments(course), instructors=content.get_users_from_role(course, "instructor"), assistants=content.get_users_from_role(course, "assistant"), registered_students=content.get_registered_students(course), result=result, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course))
        except Exception as inst:
            render_error(self, traceback.format_exc())

