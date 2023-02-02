from BaseUserHandler import *

class ExerciseSubmissionsHandler(BaseUserHandler):
    def get(self, course, assignment, exercise):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                self.render("exercise_submissions.html", courses=self.get_courses(), course_basics=self.content.get_course_basics(course), assignments=self.content.get_assignments_basics(course), assignment_basics=self.content.get_assignment_basics(course, assignment), exercise_basics=self.content.get_exercise_basics(course, assignment, exercise), exercise_submissions=self.content.get_exercise_submissions(course, assignment, exercise), user_info=self.get_user_info())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

