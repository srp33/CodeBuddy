from BaseUserHandler import *

class CopyExerciseHandler(BaseUserHandler):
    def post(self, course, assignment, exercise):
        out_dict = {"result": ""}

        try:
            if self.is_administrator() or self.is_instructor_for_course(course):
                new_title = self.get_body_argument("new_title").strip()
                existing_titles = list(map(lambda x: x[1]["title"], self.content.get_exercises(course, assignment)))

                if new_title in existing_titles:
                    out_dict["result"] = "Error: an exercise with that title already exists in this assignment."
                else:
                    self.content.copy_exercise(course, assignment, exercise, new_title)
            else:
                out_dict["result"] = "You do not have permission to copy this exercise."
        except Exception as inst:
            out_dict["result"] = traceback.format_exc()

        self.write(json.dumps(out_dict))
