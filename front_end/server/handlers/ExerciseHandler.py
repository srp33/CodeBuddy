# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class ExerciseHandler(BaseUserHandler):
    entrypoint = 'exercise'

    async def get(self, course_id, assignment_id, exercise_id):
        try:
            course_basics = await self.get_course_basics(course_id)
            assignment_basics = await self.get_assignment_basics(course_basics, assignment_id)
            exercise_basics = await self.get_exercise_basics(course_basics, assignment_basics, exercise_id)

            course_details = await self.get_course_details(course_id)
            assignment_details = await self.get_assignment_details(course_basics, assignment_id, True)
            set_assignment_due_date_passed(assignment_details)
            exercise_details = await self.get_exercise_details(course_basics, assignment_basics, exercise_id)

            show = self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id)

            exercise_statuses = self.content.get_exercise_statuses(course_id, assignment_id, self.get_current_user(), show_hidden=show)

            next_prev_exercises = self.content.get_next_prev_exercises(course_id, assignment_id, exercise_id, exercise_statuses)

            assignment_statuses = await self.get_assignment_statuses(course_basics)

            is_taking_timed_assignment, is_taking_restricted_assignment = self.content.is_taking_timed_assignment(self.get_current_user(), assignment_id)

            if not await self.check_whether_should_show_exercise(course_id, assignment_id, assignment_details, assignment_statuses, self.courses, assignment_basics, course_basics, is_taking_restricted_assignment):
                return

            # Fetches all users enrolled in a course excluding the current user as options to pair program with.
            user_list = None
            if exercise_details["enable_pair_programming"]:
                partner_info = await self.get_partner_info(course_id)
                user_list = list(partner_info.keys())
            
            timer_status = None
            timer_deadline = None
            if assignment_details["has_timer"]:
                timer_status, __, __, __, timer_deadline = get_student_timer_status(self.content, course_id, assignment_id, assignment_details, self.user_info["user_id"])

            presubmission, submissions, has_passed = self.content.get_submissions(course_id, assignment_id, exercise_id, self.get_current_user(), exercise_details)

            format_exercise_details(exercise_details, course_basics, assignment_basics, self.user_info, self.content, next_prev_exercises, format_tests=True, format_data=True)

            support_questions = self.settings_dict["smtp_server"] != "" and self.settings_dict["smtp_port"] != "" and course_details["email_address"] != "" and assignment_details["support_questions"]

            qa = []
            if support_questions:
                qa = self.content.get_answered_questions(course_id, assignment_id, exercise_id, self.current_user)

            args = {"users": user_list,
                    "courses": self.courses,
                    "assignment_statuses": assignment_statuses,
                    "course_basics": course_basics,
                    "assignment_basics": assignment_basics,
                    "assignment_details": assignment_details,
                    "exercise_basics": exercise_basics,
                    "exercise_details": exercise_details,
                    "exercise_statuses": exercise_statuses,
                    "next_exercise": next_prev_exercises["next"],
                    "prev_exercise": next_prev_exercises["previous"],
                    "submissions": submissions,
                    "domain": self.settings_dict['domain'],
                    "timer_status": timer_status,
                    "timer_deadline": timer_deadline,
                    "user_info": self.user_info,
                    "user_id": self.get_current_user(),
                    "is_administrator": self.is_administrator,
                    "is_instructor": await self.is_instructor_for_course(course_id),
                    "is_assistant": await self.is_assistant_for_course(course_id),
                    "check_for_restrict_other_assignments": course_details["check_for_restrict_other_assignments"],
                    "timer_hours": None,
                    "timer_minutes": None,
                    "has_passed": has_passed, "support_questions": support_questions,
                    "qa": qa
            }

            if exercise_details["back_end"] == "multiple_choice":
                answer_dict = json.loads(exercise_details["solution_code"])
                answer_options = [x for x in sorted(answer_dict)]

                selected_answer_indices = []

                if len(submissions) > 0:
                    answers = submissions[0]["code"].split("|")

                    solution_descriptions_dict_raw = {}
                    if exercise_details["solution_description"] != "":
                        solution_descriptions_dict_raw = json.loads(exercise_details["solution_description"])

                    solution_descriptions_dict = {}

                    # This code accounts for the possibility that answer options may no longer exist (the instructor changed them).
                    for answer in answers:
                        if answer in answer_options:
                            selected_answer_indices.append(answer_options.index(answer))

                            if answer in solution_descriptions_dict_raw:
                                solution_descriptions_dict[answer] = solution_descriptions_dict_raw[answer]

                    submissions[0]["solution_descriptions_dict"] = solution_descriptions_dict

                    if presubmission:
                        presubmission_parts = presubmission.split("sandbox_code:")

                        if len(presubmission_parts) > 1:
                            presubmission = presubmission_parts[1]
                        else:
                            presubmission = ""
                elif presubmission:
                    presubmission_parts = presubmission.split("sandbox_code:")

                    selected_answer_indices = []
                    if presubmission_parts[0] != "":
                        selected_answer_indices = [int(x) for x in presubmission_parts[0].split("|")]

                    if len(presubmission_parts) > 1:
                        presubmission = presubmission_parts[1]
                else:
                    presubmission = ""

                args["presubmission"] = presubmission
                args["selected_answer_indices"] = selected_answer_indices

                args["num_correct_options"] = sum(answer_dict.values())

                args["answer_options"] = [convert_markdown_to_html(ao) for ao in answer_options]

                # This prevents students from seeing the solution on the client side.
                exercise_details["solution_code"] = ""

                # For multiple-choice questions, we store the sandbox back end in this field.
                if exercise_details["starter_code"] != "":
                    back_end_config = get_back_end_config(exercise_details["starter_code"])

                    args["sandbox_back_end"] = exercise_details["starter_code"]
                    args["code_completion_path"] = back_end_config["code_completion_path"]
                    args["sandbox_description"] = back_end_config["sandbox_description"]

                self.render("mc_exercise.html", **args)
            else:
                tests = exercise_details["tests"]

                virtual_assistant_interactions = []
                virtual_assistant_max_per_exercise = None

                use_virtual_assistant = await should_use_virtual_assistant(self, course_id, course_details, assignment_details, exercise_basics, exercise_details, self.user_info) and not is_taking_timed_assignment

                args["thumb_status"] = -1
                if use_virtual_assistant:
                    virtual_assistant_interactions = self.content.get_virtual_assistant_interactions(course_id, assignment_id, exercise_id, self.user_info["user_id"])
                    virtual_assistant_interactions = escape_json_string(json.dumps(virtual_assistant_interactions, default=str))

                    virtual_assistant_max_per_exercise = course_details["virtual_assistant_config"]["max_per_exercise"]

                    args["thumb_status"] = await self.content.get_thumb_status(course_id, assignment_id, exercise_id, self.user_info["user_id"], "virtual_assistant")

                back_end_config = None
                if exercise_details["back_end"] != "multiple_choice":
                    back_end_config = get_back_end_config(exercise_details["back_end"])

                args["presubmission"] = presubmission
                args["back_end_description"] = back_end_config["description"]
                args["code_completion_path"] = back_end_config["code_completion_path"]
                args["tests"] = tests
                args["use_virtual_assistant"] = use_virtual_assistant
                args["virtual_assistant_interactions"] = virtual_assistant_interactions
                args["virtual_assistant_max_per_exercise"] = virtual_assistant_max_per_exercise

                self.render("exercise.html", **args)

        except Exception as inst:
            render_error(self, traceback.format_exc())