from BaseUserHandler import *
import datetime as dt

class ViewAssignmentScoresHandler(BaseUserHandler):
    def get(self, course, assignment):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                assignment_basics = self.content.get_assignment_basics(course, assignment)

                self.render("view_assignment_scores.html", courses=self.get_courses(), course_basics=self.content.get_course_basics(course), assignments=self.content.get_assignments(course), assignment_basics=assignment_basics, assignment_details=self.content.get_assignment_details(course, assignment), exercises=self.content.get_exercises(course, assignment), exercise_statuses=self.content.get_exercise_statuses(course, assignment, self.get_user_id()), scores=self.content.get_assignment_scores(course, assignment), have_timers_expired=self.content.get_all_user_assignment_expired(course, assignment), curr_datetime=dt.datetime.utcnow(), download_file_name=get_scores_download_file_name(assignment_basics), user_info=self.get_user_info())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

