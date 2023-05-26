from BaseUserHandler import *

class DeleteExerciseSubmissionsHandler(BaseUserHandler):
    def post(self, course, assignment, exercise):
        result = ""

        try:
            if self.is_administrator or self.is_instructor_for_course(course):
                self.content.delete_exercise_submissions(course, assignment, exercise)
            else:
                result = "You do not have permission to purge exercise submissions."
        except Exception as inst:
            result = traceback.format_exc()

        self.write(result)
