from BaseUserHandler import *

class CopyAssignmentHandler(BaseUserHandler):
    def post(self, course, assignment):
        result = ""

        try:
            if self.is_administrator() or self.is_instructor_for_course(course):
                new_title = self.get_body_argument("new_title").strip()

                if new_title == "":
                    result = "The title cannot be blank."
                else:
                    existing_titles = list(map(lambda x: x[1]["title"], self.content.get_assignments_basics(course)))
                    if new_title in existing_titles:
                        result = "An assignment with that title already exists in this course."
                    else:
                        self.content.copy_assignment(course, assignment, new_title)
            else:
                result = "You do not have permission to copy this assignment."
        except Exception as inst:
            result = traceback.format_exc()

        self.write(result)
