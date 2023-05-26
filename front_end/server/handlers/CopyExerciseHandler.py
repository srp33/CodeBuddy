from BaseUserHandler import *

class CopyExerciseHandler(BaseUserHandler):
    def post(self, course, assignment, exercise):
        result = ""

        try:
            if self.is_administrator or self.is_instructor_for_course(course):
                new_title = self.get_body_argument("new_title").strip()

                if new_title == "":
                    result = "The title cannot be blank."
                else:
                    course_basics = self.get_course_basics(course)

                    existing_titles = list(map(lambda x: x[1]["title"], self.content.get_exercises(course_basics, self.content.get_assignment_basics(course_basics, assignment))))
                    if new_title in existing_titles:
                        result = "An exercise with that title already exists in this assignment."
                    else:
                        self.content.copy_exercise(course, assignment, exercise, new_title)
            else:
                result = "You do not have permission to copy this exercise."
        except Exception as inst:
            result = traceback.format_exc()

        self.write(result)
