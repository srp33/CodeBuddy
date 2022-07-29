from BaseUserHandler import *

class CopyAssignmentHandler(BaseUserHandler):
    def post(self, course, assignment):
        try:
            out_dict = {}
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                out_dict["result"] = "You do not have permission to perform that task."
            else:
                new_course_id = self.get_body_argument("new_course_id")

                assignment_title = self.content.get_assignment_basics(course, assignment)["title"]
                new_course_titles = list(map(lambda x: x[1]["title"], self.content.get_assignments(new_course_id)))

                if assignment_title in new_course_titles:
                    out_dict["result"] = "Error: An assignment with this title already exists in the specified course."
                else:
                    self.content.copy_assignment(course, assignment, new_course_id)
                    out_dict["result"] = ""
        except Exception as inst:
            out_dict["result"] = traceback.format_exc()

        self.write(json.dumps(out_dict))
