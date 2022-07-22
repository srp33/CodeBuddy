from BaseUserHandler import *

class StudentExerciseHandler(BaseUserHandler):
    def get(self, course, assignment, exercise, student_id):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                courses = self.content.get_courses(True)
                assignments = self.content.get_assignments(course, True)
                exercises = self.content.get_exercises(course, assignment, True)
                course_basics = self.content.get_course_basics(course)
                assignment_basics = self.content.get_assignment_basics(course, assignment)
                exercise_basics = self.content.get_exercise_basics(course, assignment, exercise)
                assignment_details = self.content.get_assignment_details(course, assignment)
                exercise_details = self.content.get_exercise_details(course, assignment, exercise, format_content=True)
                exercise_statuses = self.content.get_exercise_statuses(course, assignment, self.get_user_info()["user_id"])
                assignment_options = [x[1] for x in self.content.get_assignments(course) if str(x[0]) != assignment]

                submissions = self.content.get_submissions(course, assignment, exercise, student_id, exercise_details)
                submissions_json = escape_json_string(json.dumps(submissions))
                num_submissions = len(submissions)

                back_end = self.settings_dict["back_ends"][exercise_details["back_end"]]
                student_info = self.content.get_user_info(student_id)
                tests_json = escape_json_string(json.dumps(exercise_details["tests"], default=str))

                self.render("student_exercise.html", student_info=student_info, student_id=student_id, courses=courses, course_basics=course_basics, assignments=assignments, assignment_basics=assignment_basics, exercises=exercises, exercise_basics=exercise_basics, assignment_details=assignment_details, exercise_details=exercise_details, tests_json=tests_json, exercise_statuses=exercise_statuses, assignment_options=assignment_options, code_completion_path=back_end["code_completion_path"], back_end_description=back_end["description"], submissions_json=submissions_json, num_submissions=num_submissions, user_info=self.get_user_info(), user_id=self.get_user_id(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course))
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

