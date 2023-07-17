from BaseUserHandler import *

class DiffHandler(BaseUserHandler):
    async def post(self):
        try:
            course_id = self.get_body_argument("course_id")
            assignment_id = self.get_body_argument("assignment_id")
            exercise_id = self.get_body_argument("exercise_id")
            expected_output = self.get_body_argument("expected_output", "")
            actual_output = self.get_body_argument("actual_output", "")
            diff_output = self.get_body_argument("diff_output", "")

            course_basics = await self.get_course_basics(course_id)
            assignment_basics = await self.get_assignment_basics(course_basics, assignment_id)
            exercise_basics = await self.get_exercise_basics(course_basics, assignment_basics, exercise_id)
            exercise_details = await self.get_exercise_details(course_basics, assignment_basics, exercise_id)

            if not course_basics["exists"] or not assignment_basics["exists"] or not exercise_basics["exists"]:
                render_error(self, "Sorry, the specified course, assignment, or exercise are not available.")
                return

            assignments = await self.get_assignments(course_basics)
            assignment_details = await self.get_assignment_details(course_basics, assignment_id)

            if not await self.check_whether_should_show_exercise(course_id, assignment_id, assignment_details, assignments, self.courses, assignment_basics, course_basics):
                return

            args = {"expected": expected_output, "actual": actual_output, "diff": diff_output}

            if exercise_details["output_type"] == "txt":
                self.render("diff_txt.html", **args)
            else:
                self.render("diff_jpg.html", **args)
        except Exception as inst:
            render_error(self, traceback.format_exc())