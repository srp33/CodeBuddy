# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *
from dateutil import parser

class SubmitHandler(BaseUserHandler):
    async def post(self, course_id, assignment_id, exercise_id):
        out_dict = {"message": "", "test_outputs": {}, "completed": False, "passed": False, "score": 0, "partner_name": None, "submission_id": ""}

        try:
            user_id = self.get_current_user()
            code = self.get_body_argument("code").replace("\r", "")
            date = parser.parse(self.get_body_argument("date"))
            partner_id = self.get_body_argument("partner_id")
            partner_id = None if partner_id == "" else partner_id

            course_basics = await self.get_course_basics(course_id)
            assignment_basics = await self.get_assignment_basics(course_basics, assignment_id)

            assignment_details = await self.get_assignment_details(course_basics, assignment_id)
            exercise_details = await self.get_exercise_details(course_basics, assignment_basics, exercise_id)

            set_assignment_due_date_passed(assignment_details)
            if assignment_details["due_date_passed"] and not assignment_details["allow_late"]:
                return self.record_error(out_dict, "ineligible: The due date has passed for this assignment.")

            if partner_id:
                partner_name = self.content.get_user_info(partner_id)['name']

                partner_prerequisite_assignments_not_completed = await self.get_prerequisite_assignments_not_completed(course_id, assignment_details, partner_id)

                if len(partner_prerequisite_assignments_not_completed) > 0:
                    return self.record_error(out_dict, f"ineligible: The specified pair-programming partner ({partner_name}) must contact the instructor to discuss this assignment. This submission has NOT been saved for either student.")

            if len(code) < exercise_details["min_solution_length"]:
                return self.record_error(out_dict, f"ineligible: Your submission is shorter than the required minimum length ({exercise_details['min_solution_length']} characters).")

            if len(code) > exercise_details["max_solution_length"]:
                return self.record_error(out_dict, f"ineligible: Your submission is longer than the maximum allowed length ({exercise_details['max_solution_length']} characters).")

            if exercise_details["max_submissions"] > 0:
                num_submissions = await self.content.get_num_submissions(course_id, assignment_id, exercise_id, user_id)
            
                if num_submissions >= exercise_details["max_submissions"]:
                    return self.record_error(out_dict, "ineligible: You have exceeded the maximum number of allowed submissions for this exercise.")
                
            if exercise_details['back_end'] == "multiple_choice":
                solutions_dict = json.loads(exercise_details["solution_code"])

                # This is what the user selected.
                answer_indexes = [int(i) for i in code.split("|")]

                # This is what the instructor marked as correct.
                correct_answer_indexes = [answer_index for answer_index, answer_option in enumerate(sorted(solutions_dict)) if solutions_dict[answer_option]]

                out_dict["completed"] = True
                out_dict["passed"] = answer_indexes == correct_answer_indexes

                # Actual answers the user chose.
                answers = [answer_option for answer_index, answer_option in enumerate(sorted(solutions_dict)) if answer_index in answer_indexes]

                out_dict["solution_descriptions_dict"] = {}
                if exercise_details["solution_description"] != "":
                    solution_descriptions_dict = json.loads(exercise_details["solution_description"])

                    solution_descriptions_dict = {answer: solution_descriptions_dict[answer] for answer in answers if answer in solution_descriptions_dict}

                    out_dict["solution_descriptions_dict"] = solution_descriptions_dict

                # We store the answer(s) as a delimited list.
                code = "|".join(answers)
                out_dict["code"] = code
            else:
                out_dict = await exec_code(self.settings_dict, code, exercise_details["verification_code"], exercise_details, True)

                out_dict["code"] = code
                out_dict["completed"] = check_test_outputs(exercise_details, out_dict["test_outputs"])
                out_dict["passed"] = out_dict["completed"]

            if out_dict["message"] == "":
                out_dict["score"] = self.calc_exercise_score(course_basics, assignment_basics, assignment_details, user_id, out_dict["passed"])

                out_dict["submission_id"] = await self.content.save_submission(course_id, assignment_id, exercise_id, user_id, code, out_dict["passed"], date, exercise_details, out_dict["test_outputs"], out_dict["score"], partner_id)

                if partner_id:
                    out_dict["partner_name"] = partner_name

                    await self.content.save_submission(course_id, assignment_id, exercise_id, partner_id, code, out_dict["passed"], date, exercise_details, out_dict["test_outputs"], out_dict["score"], user_id)

                sanitize_test_outputs(exercise_details, out_dict["test_outputs"])
        except ConnectionError as inst:
            out_dict["message"] = "error: The front-end server was unable to contact the back-end server."
            out_dict["completed"] = False
            out_dict["passed"] = False
        except ReadTimeout as inst:
            out_dict["message"] = f"error: Your solution timed out after {self.settings_dict['back_ends'][exercise_details['back_end']]['timeout_seconds']} seconds."
            out_dict["completed"] = False
            out_dict["passed"] = False
        except Exception as inst:
            out_dict["message"] = f"error: {format_output_as_html(traceback.format_exc())}"
            out_dict["completed"] = False
            out_dict["passed"] = False

        self.write(json.dumps(out_dict, default=str))

    def record_error(self, out_dict, message):
        out_dict["message"] = message
        out_dict["completed"] = False
        out_dict["passed"] = False
        out_dict["score"] = 0

        return self.write(json.dumps(out_dict, default=str))

    def calc_exercise_score(self, course_basics, assignment_basics,  assignment_details, user_id, passed):
        if passed:
            if assignment_details["due_date"] and assignment_details["due_date"] < get_current_datetime(): # It's late
                if assignment_details["allow_late"]:
                    late_percent = assignment_details["late_percent"]

                    if late_percent < 1 and self.content.student_has_late_exception(course_basics["id"], assignment_basics["id"], user_id):
                        late_percent = 1

                    return 100 * late_percent
                else:
                    return 0 # This should not be reached
            else:
                return 100
        else:
            return 0