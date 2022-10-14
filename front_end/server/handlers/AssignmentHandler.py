from BaseUserHandler import *
from datetime import datetime

class AssignmentHandler(BaseUserHandler):
    def get(self, course, assignment):
        try:
            user_start_time = self.content.get_user_assignment_start_time(course, assignment, self.get_user_info()["user_id"])
            self.render_page(course, assignment, user_start_time)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course, assignment):
        try:
            user_start_time = self.content.get_user_assignment_start_time(course, assignment, self.get_user_info()["user_id"])
            if not user_start_time:
                user_start_time = datetime.utcnow()
                self.content.set_user_assignment_start_time(course, assignment, self.get_user_info()["user_id"], user_start_time)

            self.render_page(course, assignment, user_start_time)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def render_page(self, course, assignment, user_start_time):
        if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
            assignment_basics = self.content.get_assignment_basics(course, assignment)
            courses = courses = self.get_courses(True)

            return self.render("assignment_admin.html", courses=courses, assignments=self.content.get_assignments(course, True), exercises=self.content.get_exercises(course, assignment, True), exercise_statuses=self.content.get_exercise_statuses(course, assignment, self.get_user_info()["user_id"]), course_basics=self.content.get_course_basics(course), assignment_basics=assignment_basics, assignment_details=self.content.get_assignment_details(course, assignment, True), course_options=[x[1] for x in courses if str(x[0]) != course], assignment_summary_scores=self.content.get_assignment_summary_scores(course, assignment), user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course), download_file_name=get_scores_download_file_name(assignment_basics))

        courses = self.get_courses(False)
        assignments = self.content.get_assignments(course, False)
        course_basics = self.content.get_course_basics(course)
        assignment_basics = self.content.get_assignment_basics(course, assignment)
        assignment_details = self.content.get_assignment_details(course, assignment, True)

        assignment_status = get_assignment_status(self, course, assignment_details, user_start_time)

        if assignment_status == "render":
            return self.render("assignment.html", courses=courses, assignments=assignments, exercises=self.content.get_exercises(course, assignment, False), exercise_statuses=self.content.get_exercise_statuses(course, assignment, self.get_user_info()["user_id"]), course_basics=course_basics, assignment_basics=assignment_basics,assignment_details=assignment_details, start_time=user_start_time, user_start_time=user_start_time, user_info=self.get_user_info())
        else:
            return self.render("unavailable_assignment.html", courses=courses, assignments=assignments, course_basics=course_basics, assignment_basics=assignment_basics, assignment_details=assignment_details, error=assignment_status, user_info=self.get_user_info())
