from BaseUserHandler import *

class ExerciseSubmissionsHandler(BaseUserHandler):
    def get(self, course, assignment, exercise):
        try:
            if self.is_administrator or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                course_basics = self.get_course_basics(course)
                assignment_basics = self.get_assignment_basics(course_basics, assignment)

                self.render("exercise_submissions.html", courses=self.courses, course_basics=course_basics, assignments=self.get_assignments(course_basics), assignment_basics=assignment_basics, exercise_basics=self.get_exercise_basics(course_basics, assignment_basics, exercise), exercise_submissions=self.content.get_exercise_submissions(course, assignment, exercise), user_info=self.user_info, is_administrator=self.is_administrator)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

