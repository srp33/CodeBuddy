from BaseUserHandler import *
import datetime as dt

class EditExerciseHandler(BaseUserHandler):
    def get(self, course, assignment, exercise):
        try:
            if self.is_administrator or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                course_basics = self.get_course_basics(course)
                assignment_basics = self.content.get_assignment_basics(course_basics, assignment)
                exercise_basics = self.content.get_exercise_basics(course_basics, assignment_basics, exercise)
                
                exercise_details = self.get_exercise_details(course_basics, assignment_basics, exercise)

                exercise_statuses = self.content.get_exercise_statuses(course, assignment, self.get_current_user(), current_exercise_id=exercise, show_hidden=True)

                for test_title in exercise_details["tests"]:
                    exercise_details["tests"][test_title]["txt_output"] = exercise_details["tests"][test_title]["txt_output"]
                    exercise_details["tests"][test_title]["txt_output_formatted"] = format_output_as_html(exercise_details["tests"][test_title]["txt_output"])

                next_prev_exercises = self.content.get_next_prev_exercises(course, assignment, exercise, exercise_statuses)

                self.render("edit_exercise.html", courses=self.courses, assignments=self.content.get_assignments(course_basics), exercise_statuses=exercise_statuses, course_basics=course_basics, assignment_basics=assignment_basics, exercise_basics=exercise_basics, exercise_basics_json=escape_json_string(json.dumps(exercise_basics, default=str)), exercise_details_json=escape_json_string(json.dumps(exercise_details, default=str)), next_exercise=next_prev_exercises["next"], prev_exercise=next_prev_exercises["previous"], back_ends_json=escape_json_string(json.dumps(self.settings_dict["back_ends"])), user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course), is_edit_page=True)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course, assignment, exercise):
        results = {"exercise_id": None, "message": "", "exercise_details": None}

        try:
            if self.is_administrator or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                course_basics = self.get_course_basics(course)
                assignment_basics = self.content.get_assignment_basics(course_basics, assignment)

                exercise_details = json.loads(self.request.body)

                exercise_basics = self.content.get_exercise_basics(course_basics, assignment_basics, exercise)
                exercise_basics["title"] = exercise_details.pop("title")
                exercise_basics["visible"] = exercise_details.pop("visible")

                current_time = dt.datetime.utcnow()
                if exercise_basics["exists"]:
                    exercise_details["date_created"] = self.get_exercise_details(course_basics, assignment_basics, exercise)["date_created"]
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