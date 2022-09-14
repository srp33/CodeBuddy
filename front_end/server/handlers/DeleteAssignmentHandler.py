from BaseUserHandler import *

class DeleteAssignmentHandler(BaseUserHandler):
    def post(self, course, assignment):
        result = ""

        try:
            if self.is_administrator() or self.is_instructor_for_course(course):
                self.content.delete_assignment(self.content.get_assignment_basics(course, assignment))
            else:
                result = "You do not have permission to delete this assignment."
        except Exception as inst:
            result = traceback.format_exc()

        self.write(result)
