from BaseUserHandler import *

class MoveExerciseHandler(BaseUserHandler):
    def post(self, course, assignment, exercise):
        result = ""

        try:
            if self.is_administrator() or self.is_instructor_for_course(course):
                new_assignment_id = self.get_body_argument("new_assignment_id")
                new_assignment_basics = self.content.get_assignment_basics(course, new_assignment_id)
                new_assignment_exercises = self.content.get_exercises(course, new_assignment_id, nice_sort=False)
                current_exercise_basics = self.content.get_exercise_basics(course, assignment, exercise)

                if self.content.has_duplicate_title(new_assignment_exercises, None, current_exercise_basics["title"]):
                    result = f"Error: An exercise with the title <b>{current_exercise_basics['title']}</b> already exists in the <b>{new_assignment_basics['title']}</b> assignment."
                else:
                    self.content.move_exercise(course, assignment, exercise, new_assignment_id)
            else:
                result = "You do not have permission to move this exercise."
        except Exception as inst:
            result = traceback.format_exc()

        self.write(result)
