from BaseUserHandler import *
import datetime as dt

class ResaveExercisesHandler(BaseUserHandler):
    def get(self, course_id, assignment_id):
        try:
            if self.is_administrator or self.is_instructor_for_course(course_id) or self.is_assistant_for_course(course_id):
                course_basics = self.get_course_basics(course_id)
                assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)
                exercises = self.content.get_exercises(course_basics, assignment_basics)

                output = f"<h2>Re-saving exercises for {course_basics['title']} and {assignment_basics['title']}</h2>"

                for exercise in exercises:
                    exercise_basics = self.content.get_exercise_basics(course_basics, assignment_basics, exercise[0])
                    exercise_details = self.get_exercise_details(course_basics, assignment_basics, exercise[0])
                    exercise_details["date_updated"] = dt.datetime.utcnow()

                    output += f"<p>Working on {exercise_basics['title']} (ID: {exercise_basics['id']})..."

                    result, success = execute_and_save_exercise(self.settings_dict, self.content, exercise_basics, exercise_details)

                    if success:
                        output += f"success!</p>"
                    else:
                        output += f"error occurred: {result}!</p>"

                output += "<h4>All done.</h4>"

                self.render("resave_exercises.html", courses=self.courses, assignments=self.content.get_assignments(course_basics), course_basics=course_basics, assignment_basics=assignment_basics, output=output, user_info=self.user_info, is_administrator=self.is_administrator)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())