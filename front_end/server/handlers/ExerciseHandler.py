from BaseUserHandler import *
import datetime as dt

class ExerciseHandler(BaseUserHandler):
    entrypoint = 'exercise'

    def get(self, course, assignment, exercise):
        try:
            show = self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course)

            courses = self.get_courses(show)
            assignments = self.content.get_assignments(course, show)
            exercises = self.content.get_exercises(course, assignment, show)

            course_basics = self.content.get_course_basics(course)
            assignment_basics = self.content.get_assignment_basics(course, assignment)
            exercise_basics = self.content.get_exercise_basics(course, assignment, exercise)

            assignment_details = self.content.get_assignment_details(course, assignment)
            exercise_details = self.content.get_exercise_details(course, assignment, exercise)

            if not self.is_administrator() and not self.is_instructor_for_course(course) and not self.is_assistant_for_course(course) and assignment_details["has_timer"]:
                start_time = self.content.get_user_assignment_start_time(course, assignment, self.get_user_id())

                if not start_time or self.content.has_user_assignment_start_timer_ended(course, assignment, start_time):
                    if not assignment_details["due_date"] or assignment_details["due_date"] > dt.datetime.now():
                        self.render("timer_error.html", user_info=self.content.get_user_info(self.get_user_id()))
                        return

            back_end = self.settings_dict["back_ends"][exercise_details["back_end"]]
            next_prev_exercises = self.content.get_next_prev_exercises(course, assignment, exercise, exercises)
            user_info = self.get_user_info()
            client_ip = get_client_ip_address(self.request)

            help_request = self.content.get_help_request(course, assignment, exercise, self.get_user_id())
            same_suggestion = None
            if help_request and not help_request["approved"]:
                same_suggestion = self.content.get_same_suggestion(help_request)

            if assignment_details["allowed_ip_addresses"] and client_ip not in assignment_details["allowed_ip_addresses"] and not self.is_administrator() and not self.is_instructor_for_course(course) and not self.is_assistant_for_course(course):
                self.render("unavailable_assignment.html", courses=courses, assignments=assignments, course_basics=course_basics, assignment_basics=assignment_basics, error="restricted_ip", user_info=user_info)
            elif not self.is_administrator() and not self.is_instructor_for_course(course) and not self.is_assistant_for_course(course) and user_info["user_id"] not in list(map(lambda x: x[0], self.content.get_registered_students(course))):
                self.render("unavailable_assignment.html", courses=courses, assignments=assignments, course_basics=course_basics, error="not_registered_for_course", assignment_basics=assignment_basics, user_info=user_info)
            else:
                # Fetches all users enrolled in a course excluding the current user as options to pair program with.
                user_list = list(self.content.get_partner_info(course, user_info["user_id"]).keys())
                exercise_statuses = self.content.get_exercise_statuses(course, assignment, self.get_user_id())
                start_time = self.content.get_user_assignment_start_time(course, assignment, self.get_user_id())

                tests = exercise_details["tests"]
                submissions = self.content.get_submissions(course, assignment, exercise, self.get_user_id(), exercise_details)

                format_exercise_details(exercise_details, exercise_basics, user_info["name"], self.content, next_prev_exercises, format_tests=(not user_info["use_studio_mode"]))

                args = {
                        "users": user_list,
                        "courses": courses,
                        "assignments": assignments,
                        "exercises": exercises,
                        "course_basics": course_basics,
                        "assignment_basics": assignment_basics,
                        "assignment_details": assignment_details,
                        "exercise_basics": exercise_basics,
                        "exercise_details": exercise_details,
                        "tests": tests,
                        "submissions": submissions,
                        "num_submissions": len(submissions),
                        "exercise_statuses": exercise_statuses,
                        "assignment_options": [x[1] for x in self.content.get_assignments(course) if str(x[0]) != assignment],
                        "curr_datetime": dt.datetime.now(),
                        "next_exercise": next_prev_exercises["next"],
                        "prev_exercise": next_prev_exercises["previous"],
                        "code_completion_path": back_end["code_completion_path"],
                        "back_end_description": back_end["description"],
                        "domain": self.settings_dict['domain'],
                        "start_time": start_time,
                        "user_info": user_info,
                        "user_id": self.get_user_id(),
                        "student_id": self.get_user_id(),
                        "is_administrator": self.is_administrator(),
                        "is_instructor": self.is_instructor_for_course(course),
                        "is_assistant": self.is_assistant_for_course(course),
                        "help_request": help_request,
                        "same_suggestion": same_suggestion,
                }

                if user_info["use_studio_mode"]:
                    args['presubmission'] = self.content.get_presubmission(course, assignment, exercise, self.get_user_id())

                    exercise_details['show_instructor_solution'] = bool(exercise_details['show_instructor_solution'] and (exercise_details['solution_code'] != "" or exercise_details['solution_description'] != ""))
                    del exercise_details['solution_code']
                    del exercise_details['solution_description']

                    args['exercise_details'] = exercise_details
                    self.render("spa.html", template_variables=args, **args)
                else:
                    self.render("exercise.html", **args)
        except Exception as inst:
            render_error(self, traceback.format_exc())
