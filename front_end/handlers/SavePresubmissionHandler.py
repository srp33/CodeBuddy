import sys
sys.path.append("..")
from StaticFileHandler import *
from BaseUserHandler import *
from content import *

settings_dict = load_yaml_dict(read_file("/Settings.yaml"))
content = Content(settings_dict)

class SavePresubmissionHandler(BaseUserHandler):
    def post(self, course, assignment, exercise):
        user_id = self.get_user_id()
        code = self.get_body_argument("user_code").replace("\r", "")
        content.save_presubmission(course, assignment, exercise, user_id, code)

