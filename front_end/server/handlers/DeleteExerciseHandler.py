from BaseUserHandler import *

class DeleteExerciseHandler(BaseUserHandler):
    async def post(self, course_id, assignment_id, exercise_id):
        result = ""

        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id):
                self.content.delete_exercise(course_id, assignment_id, exercise_id)
            else:
                result = "You do not have permission to delete this exercise."
        except Exception as inst:
            result = traceback.format_exc()

        self.write(result)