from BaseUserHandler import *
import datetime as dt

class CourseHandler(BaseUserHandler):
    def get(self, course):
        user_info = self.get_user_info()
        if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
            try:
                assignments = self.content.get_assignments(course, True)

                self.render("course_admin.html", courses=self.content.get_courses(True), assignments=assignments, course_basics=self.content.get_course_basics(course), course_details=self.content.get_course_details(course, True), course_scores=self.content.get_course_scores(course, assignments), user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), has_pair_programming=self.content.course_has_pair_programming(course))
            except Exception as inst:
                render_error(self, traceback.format_exc())
        elif not self.is_administrator() and not self.is_instructor_for_course(course) and not self.is_assistant_for_course(course) and user_info["user_id"] not in list(map(lambda x: x[0], self.content.get_registered_students(course))):
            self.render("unavailable_assignment.html", courses=self.content.get_courses(),
                        assignments=self.content.get_assignments(course),
                        course_basics=self.content.get_course_basics(course),
                        error="not_registered_for_course", assignment_basics=self.content.get_assignment_basics(course, None),
                        user_info=user_info)
        else:
            try:
                self.render("course.html", courses=self.content.get_courses(False), assignments=self.content.get_assignments(course, False), assignment_statuses=self.content.get_assignment_statuses(course, self.get_user_id()), course_basics=self.content.get_course_basics(course), course_details=self.content.get_course_details(course, True), curr_datetime=dt.datetime.now(), user_info=self.get_user_info(), has_pair_programming=self.content.course_has_pair_programming(course))
            except Exception as inst:
                render_error(self, traceback.format_exc())
