from BaseUserHandler import *
from datetime import datetime

class AssignmentHandler(BaseUserHandler):
    def get(self, course_id, assignment_id):
        try:
            course_basics = self.get_course_basics(course_id)
            assignment_basics = self.get_assignment_basics(course_basics, assignment_id)
            assignment_details = self.get_assignment_details(course_basics, assignment_id, True)

            user_start_time = None
            if assignment_details["has_timer"]:
                user_start_time = self.content.get_user_assignment_start_time(course_id, assignment_id, self.user_info["user_id"])
            
            self.render_page(course_basics, assignment_basics, assignment_details, user_start_time)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course_id, assignment_id):
        try:
            course_basics = self.get_course_basics(course_id)
            assignment_basics = self.get_assignment_basics(course_basics, assignment_id)
            assignment_details = self.get_assignment_details(course_basics, assignment_id, True)

            user_start_time = None
            if assignment_details["has_timer"]:
                user_start_time = self.content.get_user_assignment_start_time(course_id, assignment_id, self.user_info["user_id"])

                if not user_start_time:
                    user_start_time = datetime.utcnow()
                    self.content.set_user_assignment_start_time(course_id, assignment_id, self.user_info["user_id"], user_start_time)

            self.render_page(course_basics, assignment_basics, assignment_details, user_start_time)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def render_page(self, course_basics, assignment_basics, assignment_details, user_start_time):
        course_id = course_basics["id"]
        assignment_id = assignment_basics["id"]

        if self.is_administrator or self.is_instructor_for_course(course_id) or self.is_assistant_for_course(course_id):
            exercise_statuses = self.content.get_exercise_statuses(course_id, assignment_id, self.user_info["user_id"], show_hidden=True)
            has_non_default_weight = len([x[1]["weight"] for x in exercise_statuses if x[1]["weight"] != 1.0]) > 0

            return self.render("assignment_admin.html", courses=self.courses, assignments=self.content.get_assignments(course_basics), exercises=self.content.get_exercises(course_basics, assignment_basics, show_hidden=True), exercise_statuses=exercise_statuses, has_non_default_weight=has_non_default_weight, course_basics=course_basics, assignment_basics=assignment_basics, assignment_details=assignment_details, course_options=[x[1] for x in self.courses if str(x[0]) != course_id], assignment_summary_scores=self.content.get_assignment_summary_scores(course_basics, assignment_basics), user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=self.is_instructor_for_course(course_id), is_assistant=self.is_assistant_for_course(course_id), download_file_name=get_scores_download_file_name(assignment_basics))

        assignments = self.get_assignments(course_basics)

        assignment_status = get_assignment_status(self, course_id, assignment_details, datetime.utcnow())

        if assignment_status == "render":
            exercise_statuses = self.content.get_exercise_statuses(course_id, assignment_id, self.user_info["user_id"], show_hidden=False)
            has_non_default_weight = len([x[1]["weight"] for x in exercise_statuses if x[1]["weight"] != 1.0]) > 0

            return self.render("assignment.html", courses=self.courses, assignments=assignments, exercise_statuses=exercise_statuses, has_non_default_weight=has_non_default_weight, course_basics=course_basics, assignment_basics=assignment_basics,assignment_details=assignment_details, start_time=user_start_time, user_start_time=user_start_time, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=self.is_instructor_for_course(course_id))
        else:
            return self.render("unavailable_assignment.html", courses=self.courses, assignments=assignments, course_basics=course_basics, assignment_basics=assignment_basics, assignment_details=assignment_details, error=assignment_status, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=self.is_instructor_for_course(course_id))