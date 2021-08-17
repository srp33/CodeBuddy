from BaseUserHandler import *

class CopyAssignmentHandler(BaseUserHandler):
    def post(self, course, assignment):
        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                self.render("permissions.html")
                return

            new_course_id = self.get_body_argument("new_course_id")
            self.content.copy_assignment(course, assignment, new_course_id)
            assignment_basics = self.content.get_assignment_basics(course, assignment)

            self.render("assignment_admin.html", courses=self.content.get_courses(True), assignments=self.content.get_assignments(course, True), exercises=self.content.get_exercises(course, assignment, True), exercise_statuses=self.content.get_exercise_statuses(course, assignment, self.get_user_info()["user_id"]), course_basics=self.content.get_course_basics(course), assignment_basics=assignment_basics, assignment_details=self.content.get_assignment_details(course, assignment, True), course_options=[x[1] for x in self.content.get_courses() if str(x[0]) != course], user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course), download_file_name=get_scores_download_file_name(assignment_basics))

        except Exception as inst:
            render_error(self, traceback.format_exc())
