from BaseUserHandler import *
import datetime as dt


class ViewScoresHandler(BaseUserHandler):
    def get(self, course, assignment):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                assignment_basics = self.content.get_assignment_basics(course, assignment)

                self.render("view_scores.html", courses=self.content.get_courses(), course_basics=self.content.get_course_basics(course), assignments=self.content.get_assignments(course), assignment_basics=assignment_basics, assignment_details=self.content.get_assignment_details(course, assignment), exercises=self.content.get_exercises(course, assignment), exercise_statuses=self.content.get_exercise_statuses(course, assignment, self.get_user_id()), scores=self.content.get_assignment_scores(course, assignment), start_times=self.content.get_all_user_assignment_start_times(course, assignment), curr_datetime=dt.datetime.now(), download_file_name=get_scores_download_file_name(assignment_basics), user_info=self.get_user_info())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

