from BaseUserHandler import *

class DiffHandler(BaseUserHandler):
    def post(self):
        try:
            course_id = self.get_body_argument("course_id")
            assignment_id = self.get_body_argument("assignment_id")
            exercise_id = self.get_body_argument("exercise_id")
            expected_output = self.get_body_argument("expected_output", "")
            actual_output = self.get_body_argument("actual_output", "")
            diff_output = self.get_body_argument("diff_output", "")

            course_basics = self.content.get_course_basics(course_id)
            assignment_basics = self.content.get_assignment_basics(course_id, assignment_id)
            exercise_basics = self.content.get_exercise_basics(course_id, assignment_id, exercise_id)
            exercise_details = self.content.get_exercise_details(course_id, assignment_id, exercise_id)

            if not course_basics["exists"] or not assignment_basics["exists"] or not exercise_basics["exists"]:
                render_error(self, "Sorry, the specified course, assignment, or exercise are not available.")
                return

            show = self.is_administrator() or self.is_instructor_for_course(course_id) or self.is_assistant_for_course(course_id)

            courses = self.get_courses(show)
            assignments = self.content.get_assignments_basics(course_id, show)
            assignment_details = self.content.get_assignment_details(course_id, assignment_id)

            if not self.check_whether_should_show_exercise(course_id, assignment_id, assignment_details, assignments, courses, assignment_basics, course_basics):
                return

            args = {"expected": expected_output, "actual": actual_output, "diff": diff_output}

            if exercise_details["output_type"] == "txt":
                self.render("diff_txt.html", **args)
            else:
                self.render("diff_jpg.html", **args)
        except Exception as inst:
            render_error(self, traceback.format_exc())
