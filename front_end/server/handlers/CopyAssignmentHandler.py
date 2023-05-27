from BaseUserHandler import *

class CopyAssignmentHandler(BaseUserHandler):
    def post(self, course_id, assignment_id):
        course_basics = self.get_course_basics(course_id)
        result = ""

        try:
            if self.is_administrator or self.is_instructor_for_course(course_id):
                new_title = self.get_body_argument("new_title").strip()

                if new_title == "":
                    result = "The title cannot be blank."
                else:
                    existing_titles = list(map(lambda x: x[1]["title"], self.content.get_assignments(course_basics)))
                    if new_title in existing_titles:
                        result = "An assignment with that title already exists in this course."
                    else:
                        self.content.copy_assignment(course_id, assignment_id, new_title)
            else:
                result = "You do not have permission to copy this assignment."
        except Exception as inst:
            result = traceback.format_exc()

        self.write(result)