from BaseUserHandler import *
import datetime as dt

class ViewPairProgrammingAssignmentsHandler(BaseUserHandler):
    def get(self, course):
        user_info = self.get_user_info()

        if not self.is_administrator() and not self.is_instructor_for_course(course) and not self.is_assistant_for_course(course) and user_info["user_id"] not in list(map(lambda x: x[0], self.content.get_registered_students(course))):
            self.render("unavailable_assignment.html", courses=self.get_courses(),
                        assignments=self.content.get_assignments(course),
                        course_basics=self.content.get_course_basics(course),
                        error="not_registered_for_course", assignment_basics=self.content.get_assignment_basics(course, None),
                        user_info=user_info)
        else:
            try:
                self.render("view_pp.html", student_pairs=self.content.get_student_pairs(course, user_info['name']), courses=self.get_courses(), assignments=self.content.get_assignments(course, False), course_basics=self.content.get_course_basics(course), course_details=self.content.get_course_details(course, True), curr_datetime=dt.datetime.utcnow(), user_info=self.get_user_info(),)
            except Exception as inst:
                render_error(self, traceback.format_exc())
