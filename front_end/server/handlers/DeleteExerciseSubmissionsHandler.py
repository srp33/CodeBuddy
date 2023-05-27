from BaseUserHandler import *

class DeleteExerciseSubmissionsHandler(BaseUserHandler):
    def post(self, course_id, assignment_id, exercise_id):
        result = ""

        try:
            if self.is_administrator or self.is_instructor_for_course(course_id):
                self.content.delete_exercise_submissions(course_id, assignment_id, exercise_id)
            else:
                result = "You do not have permission to purge exercise submissions."
        except Exception as inst:
            result = traceback.format_exc()

        self.write(result)