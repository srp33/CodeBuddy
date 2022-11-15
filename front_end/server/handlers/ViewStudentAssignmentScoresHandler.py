from BaseUserHandler import *

class ViewStudentAssignmentScoresHandler(BaseUserHandler):
    def get(self, course, user_id):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                self.render("view_student_assignment_scores.html", courses=self.get_courses(), course_basics=self.content.get_course_basics(course), assignments=self.content.get_assignments(course), assignment_scores=self.content.get_student_assignment_scores(course, user_id), user_info=self.content.get_user_info(user_id))
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

