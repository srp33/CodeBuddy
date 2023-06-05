from BaseUserHandler import *

class MoveAssignmentHandler(BaseUserHandler):
    async def post(self, course_id, assignment_id):
        result = ""

        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id):
                new_course_id = self.get_body_argument("new_course_id")
                existing_course_basics = await self.get_course_basics(course_id)
                new_course_basics = await self.get_course_basics(new_course_id)
                new_course_assignments = self.content.get_assignments(new_course_basics)
                current_assignment_basics = self.content.get_assignment_basics(existing_course_basics, assignment_id)

                if self.content.has_duplicate_title(new_course_assignments, None, current_assignment_basics["title"]):
                    result = f"Error: An assignment with the title <b>{current_assignment_basics['title']}</b> already exists in the <b>{new_course_basics['title']}</b> course."
                else:
                    self.content.move_assignment(course_id, assignment_id, new_course_id)
            else:
                result = "You do not have permission to move this assignment."
        except Exception as inst:
            result = traceback.format_exc()

        self.write(result)