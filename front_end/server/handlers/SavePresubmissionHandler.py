from BaseUserHandler import *

class SavePresubmissionHandler(BaseUserHandler):
    async def post(self, course_id, assignment_id, exercise_id):
        try:
            user_id = self.get_current_user()
            code = self.get_body_argument("user_code").replace("\r", "")

            self.content.save_presubmission(course_id, assignment_id, exercise_id, user_id, code)
        except Exception as inst:
            self.write(traceback.format_exc())