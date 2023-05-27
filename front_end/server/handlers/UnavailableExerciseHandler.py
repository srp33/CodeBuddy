from BaseUserHandler import *

class UnavailableExerciseHandler(BaseUserHandler):
    def get(self, course_id, assignment_id):
        try:
            course_basics = self.get_course_basics(course_id)

            return self.render("unavailable_exercise.html", courses=self.courses, assignments=self.get_assignments(course_basics), course_basics=course_basics, assignment_basics=self.get_assignment_basics(course_basics, assignment_id), user_info=self.user_info, is_administrator=self.is_administrator)
        except Exception as inst:
            render_error(self, traceback.format_exc())