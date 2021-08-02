from .content import *
import traceback
from BaseUserHandler import *
class GetPresubmissionHandler(BaseUserHandler):
    def get(self, course, assignment, exercise, student_id):
        user_info = self.get_user_info()
        try:
            if user_info["user_id"] != student_id and not self.is_administrator() and not self.is_instructor_for_course(course) and not self.is_assistant_for_course(course):
                presubmission_info = ["Submissions may only be view by their author."]
            else:
                presubmission_info = content.get_presubmission(course, assignment, exercise, student_id)
        except:
            print(traceback.format_exc())

        self.write(json.dumps(presubmission_info))

