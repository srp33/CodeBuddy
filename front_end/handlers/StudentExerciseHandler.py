import traceback
from BaseUserHandler import *


class StudentExerciseHandler(BaseUserHandler):
    def get(self, course, assignment, exercise, student_id):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                exercises = self.content.get_exercises(course, assignment, True)
                exercise_details = self.content.get_exercise_details(course, assignment, exercise, format_self.content=True)
                back_end = settings_dict["back_ends"][exercise_details["back_end"]]
                next_prev_exercises=self.content.get_next_prev_exercises(course, assignment, exercise, exercises)

                self.render("student_exercise.html", student_info=self.content.get_user_info(student_id), student_id=student_id, courses=self.content.get_courses(True), course_basics=self.content.get_course_basics(course), assignments=self.content.get_assignments(course, True), assignment_basics=self.content.get_assignment_basics(course, assignment), exercises=exercises, exercise_basics=self.content.get_exercise_basics(course, assignment, exercise), exercise_details=exercise_details, tests=self.content.get_tests(course, assignment, exercise), next_exercise=next_prev_exercises["next"], exercise_statuses=self.content.get_exercise_statuses(course, assignment, self.get_user_info()["user_id"]), assignment_options=[x[1] for x in self.content.get_assignments(course) if str(x[0]) != assignment], code_completion_path=back_end["code_completion_path"], back_end_description=back_end["description"], num_submissions=self.content.get_num_submissions(course, assignment, exercise, student_id), user_info=self.get_user_info(), user_id=self.get_user_id(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course))
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

