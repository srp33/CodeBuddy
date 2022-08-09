from BaseUserHandler import *
import datetime as dt

class ViewInstructorSolutionHandler(BaseUserHandler):
    def get(self, course, assignment, exercise):
        try:
            client_ip = get_client_ip_address(self.request)
            user = self.get_user_id()
            user_info = self.get_user_info()

            courses = self.get_courses()
            assignments = self.content.get_assignments(course)
            exercises = self.content.get_exercises(course, assignment)
            course_basics = self.content.get_course_basics(course)
            assignment_basics = self.content.get_assignment_basics(course, assignment)
            exercise_basics = self.content.get_exercise_basics(course, assignment, exercise)
            assignment_details = self.content.get_assignment_details(course, assignment)
            exercise_details = self.content.get_exercise_details(course, assignment, exercise)
            exercise_statuses = self.content.get_exercise_statuses(course, assignment, user)
            user_code = self.content.get_most_recent_submission_code(course, assignment, exercise, user)

            if assignment_details["allowed_ip_addresses"] and client_ip not in assignment_details["allowed_ip_addresses"] and not self.is_administrator() and not self.is_instructor_for_course(course) and not self.is_assistant_for_course(course):
                self.render("unavailable_assignment.html", courses=courses, assignments=assignments, course_basics=course_basics, assignment_basics=assignment_basics, error="restricted_ip", user_info=user_info)
            else:
                format_exercise_details(exercise_details)
                add_what_students_see(exercise_details, user_info["name"])

                self.render("view_instructor_solution.html", courses=courses, assignments=assignments, exercises=exercises, course_basics=course_basics, assignment_basics=assignment_basics, assignment_details=assignment_details, exercise_basics=exercise_basics, exercise_details=exercise_details, exercise_statuses=exercise_statuses, user_code=user_code, user_info=user_info, is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course))
        except Exception as inst:
            render_error(self, traceback.format_exc())
