from BaseUserHandler import *

class ViewExerciseScoresHandler(BaseUserHandler):
    def get(self, course, assignment, exercise):
        try:
            if self.is_administrator or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                course_basics = self.get_course_basics(course)
                assignment_basics = self.content.get_assignment_basics(course_basics, assignment)

                self.render("view_exercise_scores.html", courses=self.courses, course_basics=course_basics, assignments=self.content.get_assignments(course_basics), assignment_basics=assignment_basics, exercise_basics=self.content.get_exercise_basics(course_basics, assignment_basics, exercise), exercise_scores=self.content.get_exercise_scores(course, assignment, exercise), user_info=self.user_info, is_administrator=self.is_administrator)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

