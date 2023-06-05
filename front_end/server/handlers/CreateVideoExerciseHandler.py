from BaseUserHandler import *
import datetime as dt

class CreateVideoExerciseHandler(BaseUserHandler):
    async def post(self, course_id, assignment_id):
        result = ""

        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)
                assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)

                exercise_basics = self.content.get_exercise_basics(course_basics, assignment_basics, None)
                exercise_details = await self.get_exercise_details(course_basics, assignment_basics, None)

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