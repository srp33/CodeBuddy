import sys
sys.path.append("..")
from StaticFileHandler import *
from BaseUserHandler import *
from content import *


settings_dict = load_yaml_dict(read_file("/Settings.yaml"))
content = Content(settings_dict)

class GetTestsHandler(BaseUserHandler):
    def get(self, course, assignment, exercise):
        try:
            user_info = self.get_user_info()

            if not self.is_administrator() and not self.is_instructor_for_course(course) and not self.is_assistant_for_course(course):
                self.render("permissions.html")
            else:
                tests = content.get_tests(course, assignment, exercise)
        except Exception as inst:
            tests = []

        self.write(json.dumps(tests))

