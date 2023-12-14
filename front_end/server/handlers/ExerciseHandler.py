# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class ExerciseHandler(BaseUserHandler):
    entrypoint = 'exercise'

    async def get(self, course_id, assignment_id, exercise_id):
        try:
            show = self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id)
            course_basics = await self.get_course_basics(course_id)
            course_details = await self.get_course_details(course_id)

            assignments = await self.get_assignments(course_basics)
            assignment_basics = await self.get_assignment_basics(course_basics, assignment_id)
            assignment_details = await self.get_assignment_details(course_basics, assignment_id)
            set_assignment_due_date_passed(assignment_details)

            if not await self.check_whether_should_show_exercise(course_id, assignment_id, assignment_details, assignments, self.courses, assignment_basics, course_basics):
                return

            exercise_basics = await self.get_exercise_basics(course_basics, assignment_basics, exercise_id)
            exercise_details = await self.get_exercise_details(course_basics, assignment_basics, exercise_id)
            exercise_statuses = self.content.get_exercise_statuses(course_id, assignment_id, self.get_current_user(), current_exercise_id=exercise_id, show_hidden=show)

            back_end_config = get_back_end_config(exercise_details["back_end"])

            next_prev_exercises = self.content.get_next_prev_exercises(course_id, assignment_id, exercise_id, exercise_statuses)

            # Fetches all users enrolled in a course excluding the current user as options to pair program with.
            partner_info = await self.get_partner_info(course_id, True)
            user_list = list(partner_info.keys())
            
            timer_status = None
            timer_deadline = None
            if assignment_details["has_timer"]:
                timer_status, __, __, __, timer_deadline = get_student_timer_status(self.content, course_id, assignment_id, assignment_details, self.user_info["user_id"])

            tests = exercise_details["tests"]
            presubmission, submissions, has_passed = self.content.get_submissions(course_id, assignment_id, exercise_id, self.get_current_user(), exercise_details)

            mode = self.get_query_argument("mode", default=None)

            studio_mode = self.user_info["use_studio_mode"]
            if mode == "studio":
                studio_mode = True
            elif mode == "classic":
                studio_mode = False

            virtual_assistant_interactions = []
            virtual_assistant_max_per_exercise = None

            use_virtual_assistant = course_details["virtual_assistant_config"] and await should_use_virtual_assistant(self, course_id, assignment_details, exercise_basics, self.user_info)

            if use_virtual_assistant:
                studio_mode = False

            format_exercise_details(exercise_details, course_basics, assignment_basics, self.user_info, self.content, next_prev_exercises, format_tests=True, format_data=(not studio_mode))

            if use_virtual_assistant:
                virtual_assistant_interactions = self.content.get_virtual_assistant_interactions(course_id, assignment_id, exercise_id, self.user_info["user_id"])
                virtual_assistant_interactions = escape_json_string(json.dumps(virtual_assistant_interactions, default=str))

                virtual_assistant_max_per_exercise = course_details["virtual_assistant_config"]["max_per_exercise"]

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
                    "has_passed": has_passed,
                    "exercise_statuses": exercise_statuses,
                    "next_exercise": next_prev_exercises["next"],
                    "prev_exercise": next_prev_exercises["previous"],
                    "code_completion_path": back_end_config["code_completion_path"],
                    "back_end_description": back_end_config["description"],
                    "domain": self.settings_dict['domain'],
                    "timer_status": timer_status,
                    "timer_deadline": timer_deadline,
                    "user_info": self.user_info,
                    "user_id": self.get_current_user(),
                    "is_administrator": self.is_administrator,
                    "is_instructor": await self.is_instructor_for_course(course_id),
                    "is_assistant": await self.is_assistant_for_course(course_id),
                    "check_for_restrict_other_assignments": course_details["check_for_restrict_other_assignments"],
                    "use_virtual_assistant": use_virtual_assistant,
                    "virtual_assistant_interactions": virtual_assistant_interactions,
                    "virtual_assistant_max_per_exercise": virtual_assistant_max_per_exercise
            }

#                    "num_submissions": len(submissions),

            if studio_mode:
                exercise_details['show_instructor_solution'] = bool(exercise_details['show_instructor_solution'] and (exercise_details['solution_code'] != "" or exercise_details['solution_description'] != ""))

                del exercise_details['solution_code']
                del exercise_details['solution_description']

                args['exercise_details'] = exercise_details
                self.render("spa.html", template_variables=args, **args)
            else:
                self.render("exercise.html", **args)
        except Exception as inst:
            render_error(self, traceback.format_exc())