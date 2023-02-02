from BaseUserHandler import *

class UnavailableExerciseHandler(BaseUserHandler):
    def get(self, course, assignment):
        try:
            return self.render("unavailable_exercise.html", courses=self.get_courses(False), assignments=self.content.get_assignments_basics(course, show_hidden=False), course_basics=self.content.get_course_basics(course), assignment_basics=self.content.get_assignment_basics(course, assignment), user_info=self.get_user_info())
        except Exception as inst:
            render_error(self, traceback.format_exc())