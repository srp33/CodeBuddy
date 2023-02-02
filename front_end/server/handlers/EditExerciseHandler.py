from BaseUserHandler import *
import datetime as dt

class EditExerciseHandler(BaseUserHandler):
    def get(self, course, assignment, exercise):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                exercises = self.content.get_exercises(course, assignment)

                exercise_basics = self.content.get_exercise_basics(course, assignment, exercise)
                exercise_details = self.content.get_exercise_details(course, assignment, exercise)

                for test_title in exercise_details["tests"]:
                    exercise_details["tests"][test_title]["txt_output"] = exercise_details["tests"][test_title]["txt_output"]
                    exercise_details["tests"][test_title]["txt_output_formatted"] = format_output_as_html(exercise_details["tests"][test_title]["txt_output"])

                next_prev_exercises = self.content.get_next_prev_exercises(course, assignment, exercise, exercises)

                self.render("edit_exercise.html", courses=self.get_courses(), assignments=self.content.get_assignments_basics(course), exercises=exercises, exercise_statuses=self.content.get_exercise_statuses(course, assignment, self.get_user_info()["user_id"]), course_basics=self.content.get_course_basics(course), assignment_basics=self.content.get_assignment_basics(course, assignment), exercise_basics=exercise_basics, exercise_basics_json=escape_json_string(json.dumps(exercise_basics, default=str)), exercise_details_json=escape_json_string(json.dumps(exercise_details, default=str)), next_exercise=next_prev_exercises["next"], prev_exercise=next_prev_exercises["previous"], back_ends_json=escape_json_string(json.dumps(self.settings_dict["back_ends"])), user_info=self.get_user_info(), is_assistant=self.is_assistant_for_course(course), is_edit_page=True)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course, assignment, exercise):
        results = {"exercise_id": None, "message": "", "exercise_details": None}

        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                exercise_details = json.loads(self.request.body)

                exercise_basics = self.content.get_exercise_basics(course, assignment, exercise)
                exercise_basics["title"] = exercise_details.pop("title")
                exercise_basics["visible"] = exercise_details.pop("visible")

                current_time = dt.datetime.utcnow()
                if exercise_basics["exists"]:
                    exercise_details["date_created"] = self.content.get_exercise_details(course, assignment, exercise)["date_created"]
                else:
                    exercise_details["date_created"] = current_time
                exercise_details["date_updated"] = current_time

                result, success = execute_and_save_exercise(self.settings_dict, self.content, exercise_basics, exercise_details)

                if success:
                    results["exercise_id"] = result
                    results["exercise_details"] = exercise_details
                else:
                    results["message"] = result
            else:
                results["message"] = "You must be an administrator or an instructor for this course to edit exercises."
        except ConnectionError as inst:
            results["message"] = "The front-end server was unable to contact the back-end server."
        except ReadTimeout as inst:
            results["message"] = "Your solution timed out when attempting to contact the back-end server."
        except Exception as inst:
            results["message"] = traceback.format_exc()

        try:
            self.write(json.dumps(results, default=str))
        except:
            results = {"exercise_id": None, "message": traceback.format_exc(), "exercise_details": None}
            self.write(json.dumps(results))
