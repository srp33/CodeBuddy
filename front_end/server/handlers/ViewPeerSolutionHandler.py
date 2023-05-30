from BaseUserHandler import *
import datetime as dt

class ViewPeerSolutionHandler(BaseUserHandler):
    def get(self, course_id, assignment_id, exercise_id):
        try:
            #client_ip = get_client_ip_address(self.request)
            user_info = self.user_info

            course_basics = self.get_course_basics(course_id)
            assignments = self.get_assignments(course_basics)
            course_details = self.get_course_details(course_id)
            
            assignment_basics = self.get_assignment_basics(course_basics, assignment_id)
            exercise_basics = self.get_exercise_basics(course_basics, assignment_basics, exercise_id)

            assignment_details = self.get_assignment_details(course_basics, assignment_id)
            exercise_details = self.get_exercise_details(course_basics, assignment_basics, exercise_id)

            exercise_statuses = self.content.get_exercise_statuses(course_id, assignment_id, user_info["user_id"])

            user_code = self.content.get_most_recent_submission_code(course_id, assignment_id, exercise_id, user_info["user_id"])
            peer_code = self.content.get_peer_code(course_id, assignment_id, exercise_id, user_info["user_id"])

            if not self.check_whether_should_show_exercise(course_id, assignment_id, assignment_details, assignments, self.courses, assignment_basics, course_basics):
                return
            else:
                next_prev_exercises = self.content.get_next_prev_exercises(course_id, assignment_id, exercise_id, exercise_statuses)

                format_exercise_details(exercise_details, course_id, assignment_id, user_info, self.content)
                self.render("view_peer_solution.html", courses=self.courses, assignments=assignments, course_basics=course_basics, assignment_basics=assignment_basics, assignment_details=assignment_details, exercise_basics=exercise_basics, exercise_details=exercise_details, exercise_statuses=exercise_statuses, next_exercise=next_prev_exercises["next"],prev_exercise=next_prev_exercises["previous"],  user_code=user_code, peer_code=peer_code, user_info=user_info, check_for_restrict_other_assignments=course_details["check_for_restrict_other_assignments"], is_administrator=self.is_administrator, is_instructor=self.is_instructor_for_course(course_id), is_assistant=self.is_assistant_for_course(course_id))
        except Exception as inst:
            render_error(self, traceback.format_exc())