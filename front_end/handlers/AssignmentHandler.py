from helper import *
import traceback
from BaseUserHandler import *
import datetime as dt
from content import *


class AssignmentHandler(BaseUserHandler):
    def get(self, course, assignment):
        if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
            try:
                assignment_basics = content.get_assignment_basics(course, assignment)

                self.render("assignment_admin.html", courses=content.get_courses(True), assignments=content.get_assignments(course, True), exercises=content.get_exercises(course, assignment, True), exercise_statuses=content.get_exercise_statuses(course, assignment, self.get_user_info()["user_id"]), course_basics=content.get_course_basics(course), assignment_basics=assignment_basics, assignment_details=content.get_assignment_details(course, assignment, True), course_options=[x[1] for x in content.get_courses() if str(x[0]) != course], user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course), download_file_name=get_scores_download_file_name(assignment_basics))
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            try:
                user_info = self.get_user_info()
                assignment_details = content.get_assignment_details(course, assignment, True)
                curr_datetime = dt.datetime.now()
                start_time = content.get_user_assignment_start_time(course, assignment, user_info["user_id"])
                client_ip = get_client_ip_address(self.request)

                if assignment_details["allowed_ip_addresses"] and client_ip not in assignment_details["allowed_ip_addresses"]:
                    self.render("unavailable_assignment.html", courses=content.get_courses(),
                                assignments=content.get_assignments(course),
                                course_basics=content.get_course_basics(course),
                                assignment_basics=content.get_assignment_basics(course, assignment), error="restricted_ip",
                                user_info=user_info)
                elif assignment_details["start_date"] and assignment_details["start_date"] > curr_datetime:
                    self.render("unavailable_assignment.html", courses=content.get_courses(), assignments=content.get_assignments(course), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), error="start", start_date=assignment_details["start_date"].strftime("%c"), user_info=user_info)
                elif assignment_details["due_date"] and assignment_details["due_date"] < curr_datetime and not assignment_details["allow_late"] and not assignment_details["view_answer_late"]:
                    self.render("unavailable_assignment.html", courses=content.get_courses(), assignments=content.get_assignments(course), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), error="due", due_date=assignment_details["due_date"].strftime("%c"), user_info=user_info)
                elif not self.is_administrator() and not self.is_instructor_for_course(course) and not self.is_assistant_for_course(course) and user_info["user_id"] not in list(map(lambda x: x[0], content.get_registered_students(course))):
                    self.render("unavailable_assignment.html", courses=content.get_courses(),
                                assignments=content.get_assignments(course),
                                course_basics=content.get_course_basics(course),
                                error="not_registered_for_course", assignment_basics=content.get_assignment_basics(course, assignment),
                                user_info=user_info)
                else:
                    self.render("assignment.html", courses=content.get_courses(False), assignments=content.get_assignments(course, False), exercises=content.get_exercises(course, assignment, False), exercise_statuses=content.get_exercise_statuses(course, assignment, user_info["user_id"]), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), assignment_details=assignment_details, curr_datetime=curr_datetime, start_time=start_time, user_info=user_info)

            except Exception as inst:
                render_error(self, traceback.format_exc())

    def post(self, course, assignment):
        try:
            show = self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course)
            user_info = self.get_user_info()
            start_time = self.get_body_argument("start_time")
            content.set_user_assignment_start_time(course, assignment, user_info["user_id"], start_time)

            self.render("assignment.html", courses=content.get_courses(show), assignments=content.get_assignments(course, show), exercises=content.get_exercises(course, assignment, show), exercise_statuses=content.get_exercise_statuses(course, assignment, user_info["user_id"]), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), assignment_details=content.get_assignment_details(course, assignment, True), curr_datetime=dt.datetime.now(), start_time=content.get_user_assignment_start_time(course, assignment, user_info["user_id"]), user_info=user_info)
        except Exception as inst:
            render_error(self, traceback.format_exc())

