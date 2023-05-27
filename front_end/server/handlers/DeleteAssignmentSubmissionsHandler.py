from BaseUserHandler import *

class DeleteAssignmentSubmissionsHandler(BaseUserHandler):
    def post(self, course_id, assignment_id):
        result = ""

        try:
            if self.is_administrator or self.is_instructor_for_course(course_id):
                self.content.delete_assignment_submissions(self.content.get_assignment_basics(self.get_course_basics(course_id), assignment_id))
            else:
                result = "You do not have permission to purge exercise submissions."
        except Exception as inst:
            result = traceback.format_exc()

        self.write(result)
