from BaseUserHandler import *
from datetime import datetime, timedelta

class ExerciseHandler(BaseUserHandler):
    entrypoint = 'exercise'

    def get(self, course_id, assignment_id, exercise_id):
        try:
            show = self.is_administrator or self.is_instructor_for_course(course_id) or self.is_assistant_for_course(course_id)
            course_basics = self.get_course_basics(course_id)
            course_details = self.get_course_details(course_id)

            assignments = self.get_assignments(course_basics)
            assignment_basics = self.get_assignment_basics(course_basics, assignment_id)
            assignment_details = self.get_assignment_details(course_basics, assignment_id)

            if not self.check_whether_should_show_exercise(course_id, assignment_id, assignment_details, assignments, self.courses, assignment_basics, course_basics):
                return

            exercise_basics = self.get_exercise_basics(course_basics, assignment_basics, exercise_id)
            exercise_details = self.get_exercise_details(course_basics, assignment_basics, exercise_id)
            exercise_statuses = self.content.get_exercise_statuses(course_id, assignment_id, self.get_current_user(), current_exercise_id=exercise_id, show_hidden=show)

            back_end = self.settings_dict["back_ends"][exercise_details["back_end"]]

            next_prev_exercises = self.content.get_next_prev_exercises(course_id, assignment_id, exercise_id, exercise_statuses)

            # help_request = self.content.get_help_request(course, assignment, exercise, self.get_user_id())
            # same_suggestion = None
            # if help_request and not help_request["approved"]:
            #     same_suggestion = self.content.get_same_suggestion(help_request)

            # Fetches all users enrolled in a course excluding the current user as options to pair program with.
            user_list = list(self.get_partner_info(course_id, True).keys())
            
            start_time = None
            if assignment_details["has_timer"]:
                start_time = self.content.get_user_assignment_start_time(course_id, assignment_id, self.get_current_user())

            tests = exercise_details["tests"]
            presubmission, submissions = self.content.get_submissions(course_id, assignment_id, exercise_id, self.get_current_user(), exercise_details)

            mode = self.get_query_argument("mode", default=None)

            studio_mode = self.user_info["use_studio_mode"]
            if mode == "studio":
                studio_mode = True
            elif mode == "classic":
                studio_mode = False

            format_exercise_details(exercise_details, course_id, assignment_id, self.user_info["name"], self.content, next_prev_exercises, format_tests=False)

            args = {
                    "users": user_list,
                    "courses": self.courses,
                    "assignments": assignments,
                    "course_basics": course_basics,
                    "assignment_basics": assignment_basics,
                    "assignment_details": assignment_details,
                    "exercise_basics": exercise_basics,
                    "exercise_details": exercise_details,
                    "tests": tests,
                    "presubmission": presubmission,
                    "submissions": submissions,
                    "exercise_statuses": exercise_statuses,
                    "next_exercise": next_prev_exercises["next"],
                    "prev_exercise": next_prev_exercises["previous"],
                    "code_completion_path": back_end["code_completion_path"],
                    "back_end_description": back_end["description"],
                    "domain": self.settings_dict['domain'],
                    "start_time": start_time,
                    "user_info": self.user_info,
                    "user_id": self.get_current_user(),
                    "is_administrator": self.is_administrator,
                    "is_instructor": self.is_instructor_for_course(course_id),
                    "is_assistant": self.is_assistant_for_course(course_id),
                    "check_for_restrict_other_assignments": course_details["check_for_restrict_other_assignments"],
                    "help_request": None,
                    "same_suggestion": None,
            }

#                    "num_submissions": len(submissions),
                    # "help_request": help_request,
                    # "same_suggestion": same_suggestion,

            if studio_mode:
                #TODO: Remove when we know it is working the other way
                #args['presubmission'] = self.content.get_presubmission(course, assignment, exercise, self.get_user_id())

                exercise_details['show_instructor_solution'] = bool(exercise_details['show_instructor_solution'] and (exercise_details['solution_code'] != "" or exercise_details['solution_description'] != ""))
                del exercise_details['solution_code']
                del exercise_details['solution_description']

                args['exercise_details'] = exercise_details
                self.render("spa.html", template_variables=args, **args)
            else:
                self.render("exercise.html", **args)
        except Exception as inst:
            render_error(self, traceback.format_exc())