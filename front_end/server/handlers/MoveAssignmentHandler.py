from BaseUserHandler import *

class MoveAssignmentHandler(BaseUserHandler):
    def post(self, course, assignment):
        result = ""

        try:
            if self.is_administrator() or self.is_instructor_for_course(course):
                new_course_id = self.get_body_argument("new_course_id")
                new_course_basics = self.content.get_course_basics(new_course_id)
                new_course_assignments = self.content.get_assignments(new_course_id, nice_sort=False)
                current_assignment_basics = self.content.get_assignment_basics(course, assignment)

                if self.content.has_duplicate_title(new_course_assignments, None, current_assignment_basics["title"]):
                    result = f"Error: An assignment with the title <b>{current_assignment_basics['title']}</b> already exists in the <b>{new_course_basics['title']}</b> course."
                else:
                    self.content.move_assignment(course, assignment, new_course_id)
            else:
                result = "You do not have permission to move this assignment."
        except Exception as inst:
            result = traceback.format_exc()

        self.write(result)
