from BaseUserHandler import *

class ViewStudentAssignmentScoresHandler(BaseUserHandler):
    async def get(self, course_id, user_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)

                self.render("view_student_assignment_scores.html", courses=self.courses, course_basics=course_basics, assignments=self.content.get_assignments(course_basics), assignment_scores=self.content.get_student_assignment_scores(course_id, user_id), user_info=self.content.get_user_info(user_id), is_administrator=self.is_administrator)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())