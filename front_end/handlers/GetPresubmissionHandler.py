from BaseUserHandler import *

class GetPresubmissionHandler(BaseUserHandler):
    def get(self, course, assignment, exercise, student_id):
        user_info = self.get_user_info()

        try:
            if user_info["user_id"] == student_id or self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                presubmission_info = self.content.get_presubmission(course, assignment, exercise, student_id)

                if presubmission_info:
                    self.write(presubmission_info)
        except:
            print(traceback.format_exc())
