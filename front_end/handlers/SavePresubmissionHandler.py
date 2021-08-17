from BaseUserHandler import *

class SavePresubmissionHandler(BaseUserHandler):
    def post(self, course, assignment, exercise):
        user_id = self.get_user_id()
        code = self.get_body_argument("user_code").replace("\r", "")
        self.content.save_presubmission(course, assignment, exercise, user_id, code)

