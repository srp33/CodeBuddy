import traceback
from BaseUserHandler import *
from content import *


class CopyExerciseHandler(BaseUserHandler):
    def post(self, course, assignment, exercise):
        out_dict = {"result": ""}
        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                self.render("permissions.html")
                return

            new_title = self.get_body_argument("new_title").strip()
            existing_titles = list(map(lambda x: x[1]["title"], content.get_exercises(course, assignment)))
            if new_title in existing_titles:
                out_dict["result"] = "Error: an exercise with that title already exists in this assignment."
            else:
                content.copy_exercise(course, assignment, exercise, new_title)
        except Exception as inst:
            out_dict["result"] = traceback.format_exc()
        self.write(json.dumps(out_dict))

