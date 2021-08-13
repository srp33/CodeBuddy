from BaseUserHandler import *
import datetime as dt

class CreateVideoExerciseHandler(BaseUserHandler):
    def post(self, course, assignment):
        response_dict = {"message": ""}

        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                response_dict["message"] = "You do not have permissions to perform this operation."
                return

            exercise_basics = self.content.get_exercise_basics(course, assignment, None)
            exercise_details = self.content.get_exercise_details(course, assignment, None)

            exercise_basics["title"] = self.get_body_argument("title")
            exercise_details["instructions"] = self.get_body_argument("instructions")
            exercise_details["back_end"] = "any_response"
            created_date = dt.datetime.now()
            exercise_details["date_updated"] = created_date
            exercise_details["date_created"] = created_date

            exercise = self.content.save_exercise(exercise_basics, exercise_details)
        except Exception as inst:
            response_dict["message"] = traceback.format_exc()

        self.write(json.dumps(response_dict));

