from BaseUserHandler import *
import datetime as dt

class CourseHandler(BaseUserHandler):
    def get(self, course_id):
        course_basics = self.get_course_basics(course_id)

        if self.is_administrator or self.is_instructor_for_course(course_id) or self.is_assistant_for_course(course_id):
            try:
                assignments = self.content.get_assignments(course_basics)

                self.render("course_admin.html", courses=self.courses, assignments=assignments, assignment_statuses=self.content.get_assignment_statuses(course_id, self.get_current_user(), True), course_basics=course_basics, course_details=self.get_course_details(course_id, True), course_summary_scores=self.content.get_course_summary_scores(course_id, assignments), user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=self.is_instructor_for_course(course_id), is_assistant=self.is_assistant_for_course(course_id))
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            try:
                user_is_registered = False
                for course in self.courses:
                    if int(course_id) == course[0]:
                        user_is_registered = True

                if user_is_registered:
                    self.render("course.html", courses=self.courses, assignments=self.get_assignments(course_basics), assignment_statuses=self.content.get_assignment_statuses(course_id, self.get_current_user(), False), course_basics=course_basics, course_details=self.get_course_details(course_id, True), curr_datetime=dt.datetime.utcnow(), user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=self.is_instructor_for_course(course_id))
                else:
                    self.render("unavailable_course.html", courses=self.courses, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=self.is_instructor_for_course(course_id))
            except Exception as inst:
                render_error(self, traceback.format_exc())