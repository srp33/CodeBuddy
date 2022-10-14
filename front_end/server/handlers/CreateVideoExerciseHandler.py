from BaseUserHandler import *
import datetime as dt

class CreateVideoExerciseHandler(BaseUserHandler):
    def post(self, course, assignment):
        result = ""

        try:
            if self.is_administrator() or self.is_instructor_for_course(course):
                exercise_basics = self.content.get_exercise_basics(course, assignment, None)
                exercise_details = self.content.get_exercise_details(course, assignment, None)

                exercise_basics["title"] = self.get_body_argument("title")
                exercise_details["instructions"] = self.get_body_argument("instructions")
                exercise_details["back_end"] = "not_code"
                exercise_details["allow_any_response"] = True
                created_date = dt.datetime.utcnow()
                exercise_details["date_updated"] = created_date
                exercise_details["date_created"] = created_date

                exercise = self.content.save_exercise(exercise_basics, exercise_details)
            else:
                result = "You do not have permissions to perform this operation."
        except Exception as inst:
            result = traceback.format_exc()

        self.write(result);

