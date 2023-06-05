from BaseUserHandler import *

class ExerciseSubmissionsHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id, exercise_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)
                assignment_basics = await self.get_assignment_basics(course_basics, assignment_id)
                exercise_basics = await self.get_exercise_basics(course_basics, assignment_basics, exercise_id)

                self.render("exercise_submissions.html", courses=self.courses, course_basics=course_basics, assignments=await self.get_assignments(course_basics), assignment_basics=assignment_basics, exercise_basics=exercise_basics, exercise_submissions=self.content.get_exercise_submissions(course_id, assignment_id, exercise_id), user_info=self.user_info, is_administrator=self.is_administrator)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())