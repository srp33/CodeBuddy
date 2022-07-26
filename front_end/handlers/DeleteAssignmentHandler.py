from BaseUserHandler import *

class DeleteAssignmentHandler(BaseUserHandler):
    def post(self, course, assignment):
        out_dict = {"result": ""}

        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                out_dict["result"] = "You do not have permission to perform this task."
            else:
                self.content.delete_assignment(self.content.get_assignment_basics(course, assignment))
        except Exception as inst:
            out_dict["result"] = traceback.format_exc()

        self.write(json.dumps(out_dict))
