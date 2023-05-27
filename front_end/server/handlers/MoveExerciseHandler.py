from BaseUserHandler import *

class MoveExerciseHandler(BaseUserHandler):
    def post(self, course_id, assignment_id, exercise_id):
        result = ""

        try:
            if self.is_administrator or self.is_instructor_for_course(course_id):
                existing_course_basics = self.get_course_basics(course_id)
                existing_assignment_basics = self.content.get_assignment_basics(existing_course_basics, assignment_id)
                existing_exercise_basics = self.content.get_exercise_basics(existing_course_basics, existing_assignment_basics, exercise_id)

                new_assignment_id = self.get_body_argument("new_assignment_id")
                new_assignment_basics = self.content.get_assignment_basics(existing_course_basics, new_assignment_id)
                new_assignment_exercises = self.content.get_exercises(existing_course_basics, new_assignment_basics)


                if self.content.has_duplicate_title(new_assignment_exercises, None, existing_exercise_basics["title"]):
                    result = f"Error: An exercise with the title <b>{existing_exercise_basics['title']}</b> already exists in the <b>{new_assignment_basics['title']}</b> assignment."
                else:
                    self.content.move_exercise(course_id, assignment_id, exercise_id, new_assignment_id)
            else:
                result = "You do not have permission to move this exercise."
        except Exception as inst:
            result = traceback.format_exc()

        self.write(result)