from BaseUserHandler import *

class StudentExerciseHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id, exercise_id, student_id):
        try:
            if self.is_administrator or self.is_instructor_for_course(course_id) or self.is_assistant_for_course(course_id):
                course_basics = self.get_course_basics(course_id)
                assignments = self.get_assignments(course_basics)
                assignment_basics = self.get_assignment_basics(course_basics, assignment_id)
                exercise_basics = await self.get_exercise_basics(course_basics, assignment_basics, exercise_id)

                assignment_details = self.get_assignment_details(course_basics, assignment_id)
                exercise_details = self.get_exercise_details(course_basics, assignment_basics, exercise_id)

                ignore_presubmission, submissions = self.content.get_submissions(course_id, assignment_id, exercise_id, student_id, exercise_details)
                num_submissions = len(submissions)

                back_end_config = get_back_end_config(exercise_details["back_end"])
                student_info = self.content.get_user_info(student_id)

                tests = exercise_details["tests"]
                format_exercise_details(exercise_details, course_id, assignment_id, student_info, self.content)

                self.render("student_exercise.html", student_info=student_info, student_id=student_id, courses=self.courses, course_basics=course_basics, assignments=assignments, assignment_basics=assignment_basics, exercise_basics=exercise_basics, assignment_details=assignment_details, exercise_details=exercise_details, tests=tests, code_completion_path=back_end_config["code_completion_path"], back_end_description=back_end_config["description"], submissions=submissions, num_submissions=num_submissions, user_info=self.user_info, user_id=self.get_current_user(), next_prev_student_ids = self.content.get_next_prev_student_ids(course_id, student_id), is_administrator=self.is_administrator, is_instructor=self.is_instructor_for_course(course_id), is_assistant=self.is_assistant_for_course(course_id))
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())