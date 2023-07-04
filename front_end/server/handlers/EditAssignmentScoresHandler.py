from BaseUserHandler import *

class EditAssignmentScoresHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id, student_id):
        try:
            course_basics = await self.get_course_basics(course_id)
            assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)

            if self.is_administrator or await self.is_instructor_for_course(course_id):
                self.render("edit_assignment_scores.html", student_id=student_id, courses=self.courses, course_basics=course_basics, assignments=self.content.get_assignments(course_basics), assignment_basics=assignment_basics, exercise_statuses=self.content.get_exercise_statuses(course_id, assignment_id, student_id, show_hidden=False), result=None, user_info=self.user_info, is_administrator=self.is_administrator)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def post(self, course_id, assignment_id, student_id):
        try:
            course_basics = await self.get_course_basics(course_id)
            assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)

            if self.is_administrator or await self.is_instructor_for_course(course_id):
                exercise_statuses = self.content.get_exercise_statuses(course_id, assignment_id, student_id, show_hidden=False)
                result = ""
                for exercise in exercise_statuses:
                    student_score = self.get_body_argument(str(exercise[1]["id"]))
                    if (student_score.isnumeric()):
                        result = f"Success: {student_id}'s scores for this assignment have been updated."
                        self.content.save_exercise_score(course_id, assignment_id, exercise[1]["id"], student_id, int(student_score))
                    else:
                        result = "Error: Newly entered scores must be numeric."

                self.render("edit_assignment_scores.html", student_id=student_id, courses=self.courses, course_basics=course_basics, assignments=await self.get_assignments(course_basics), assignment_basics=assignment_basics, exercise_statuses=self.content.get_exercise_statuses(course_id, assignment_id, student_id, show_hidden=False), result=result, user_info=self.user_info, is_administrator=self.is_administrator)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())