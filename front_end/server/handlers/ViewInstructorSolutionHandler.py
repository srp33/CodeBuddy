from BaseUserHandler import *
import datetime as dt

class ViewInstructorSolutionHandler(BaseUserHandler):
    def get(self, course, assignment, exercise):
        try:
            #client_ip = get_client_ip_address(self.request)
            user_info = self.get_user_info()

            courses = self.get_courses()
            assignments = self.content.get_assignments_basics(course)
            exercises = self.content.get_exercises(course, assignment)
            course_basics = self.content.get_course_basics(course)
            assignment_basics = self.content.get_assignment_basics(course, assignment)
            exercise_basics = self.content.get_exercise_basics(course, assignment, exercise)
            assignment_details = self.content.get_assignment_details(course, assignment)
            exercise_details = self.content.get_exercise_details(course, assignment, exercise)
            exercise_statuses = self.content.get_exercise_statuses(course, assignment, user_info["user_id"])
            user_code = self.content.get_most_recent_submission_code(course, assignment, exercise, user_info["user_id"])

            if not self.check_whether_should_show_exercise(course, assignment, assignment_details, assignments, courses, assignment_basics, course_basics):
                return
            else:
                format_exercise_details(exercise_details, exercise_basics, user_info["name"], self.content)
                self.render("view_instructor_solution.html", courses=courses, assignments=assignments, exercises=exercises, course_basics=course_basics, assignment_basics=assignment_basics, assignment_details=assignment_details, exercise_basics=exercise_basics, exercise_details=exercise_details, exercise_statuses=exercise_statuses, user_code=user_code, user_info=user_info, check_for_restrict_other_assignments=self.content.check_for_restrict_other_assignments(course), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course))
        except Exception as inst:
            render_error(self, traceback.format_exc())
