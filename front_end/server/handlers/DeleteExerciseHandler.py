from BaseUserHandler import *

class DeleteExerciseHandler(BaseUserHandler):
    def post(self, course, assignment, exercise):
        result = ""

        try:
            if self.is_administrator or self.is_instructor_for_course(course):
                self.content.delete_exercise(course, assignment, exercise)
            else:
                result = "You do not have permission to delete this exercise."
        except Exception as inst:
            result = traceback.format_exc()

        self.write(result)
