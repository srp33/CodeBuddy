import traceback
from BaseUserHandler import *
import datetime as dt


class ExerciseHandler(BaseUserHandler):
    def get(self, course, assignment, exercise):
        try:
            assignment_details = self.content.get_assignment_details(course, assignment)

            if not self.is_administrator() and not self.is_instructor_for_course(course) and not self.is_assistant_for_course(course) and assignment_details["has_timer"]:
                start_time = self.content.get_user_assignment_start_time(course, assignment, self.get_user_id())

                if not start_time or self.content.has_user_assignment_start_timer_ended(course, assignment, start_time):
                    if not assignment_details["due_date"] or assignment_details["due_date"] > dt.datetime.now():
                        self.render("timer_error.html", user_info=self.content.get_user_info(self.get_user_id()))
                        return

            show = self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course)
            exercises = self.content.get_exercises(course, assignment, show)
            exercise_details = self.content.get_exercise_details(course, assignment, exercise, format_content=True)
            exercise_details["expected_text_output"] = format_output_as_html(exercise_details["expected_text_output"])
            back_end = self.settings_dict["back_ends"][exercise_details["back_end"]]
            next_prev_exercises = self.content.get_next_prev_exercises(course, assignment, exercise, exercises)
            user_info = self.get_user_info()
            client_ip = get_client_ip_address(self.request)

            help_request = self.content.get_help_request(course, assignment, exercise, self.get_user_id())
            same_suggestion = None
            if help_request and not help_request["approved"]:
                same_suggestion = self.content.get_same_suggestion(help_request)

            if assignment_details["allowed_ip_addresses"] and client_ip not in assignment_details["allowed_ip_addresses"] and not self.is_administrator() and not self.is_instructor_for_course(course) and not self.is_assistant_for_course(course):
                self.render("unavailable_assignment.html", courses=self.content.get_courses(),
                            assignments=self.content.get_assignments(course),
                            course_basics=self.content.get_course_basics(course),
                            assignment_basics=self.content.get_assignment_basics(course, assignment), error="restricted_ip",
                            user_info=user_info)
            elif not self.is_administrator() and not self.is_instructor_for_course(course) and not self.is_assistant_for_course(course) and user_info["user_id"] not in list(map(lambda x: x[0], self.content.get_registered_students(course))):
                self.render("unavailable_assignment.html", courses=self.content.get_courses(),
                            assignments=self.content.get_assignments(course),
                            course_basics=self.content.get_course_basics(course),
                            error="not_registered_for_course", assignment_basics=self.content.get_assignment_basics(course, assignment),
                            user_info=user_info)
            else:
                # Fetches all users enrolled in a course excluding the current user as options to pair program with.
                user_list = list(self.content.get_partner_info(course, self.get_user_info()["user_id"]).keys())

                self.render("exercise.html", users=user_list, courses=self.content.get_courses(show), assignments=self.content.get_assignments(course, show), exercises=exercises, course_basics=self.content.get_course_basics(course), assignment_basics=self.content.get_assignment_basics(course, assignment), assignment_details=self.content.get_assignment_details(course, assignment), exercise_basics=self.content.get_exercise_basics(course, assignment, exercise), exercise_details=exercise_details, exercise_statuses=self.content.get_exercise_statuses(course, assignment, self.get_user_id()), assignment_options=[x[1] for x in self.content.get_assignments(course) if str(x[0]) != assignment], curr_datetime=dt.datetime.now(), next_exercise=next_prev_exercises["next"], prev_exercise=next_prev_exercises["previous"], code_completion_path=back_end["code_completion_path"], back_end_description=back_end["description"], num_submissions=self.content.get_num_submissions(course, assignment, exercise, self.get_user_id()), domain=self.settings_dict['domain'], start_time=self.content.get_user_assignment_start_time(course, assignment, self.get_user_id()), help_request=help_request, same_suggestion=same_suggestion, user_info=self.get_user_info(), user_id=self.get_user_id(), student_id=self.get_user_id(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course))

        except Exception as inst:
            render_error(self, traceback.format_exc())

