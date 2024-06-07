# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *
from dateutil import parser

class SubmitHandler(BaseUserHandler):
    async def post(self, course_id, assignment_id, exercise_id):
        out_dict = {"message": "", "test_outputs": {}, "all_passed": False, "score": 0, "partner_name": None, "submission_id": ""}

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

            if exercise_details["max_submissions"] > 0:
                num_submissions = await self.content.get_num_submissions(course_id, assignment_id, exercise_id, user_id)
            
                if num_submissions >= exercise_details["max_submissions"]:
                    out_dict["message"] = "ineligible: You have exceeded the maximum number of allowed submissions for this exercise."
                    return self.write(json.dumps(out_dict, default=str))
                
            set_assignment_due_date_passed(assignment_details)
            if assignment_details["due_date_passed"] and not assignment_details["allow_late"]:
                out_dict["message"] = "ineligible: The due date has passed for this assignment."
                
                return self.write(json.dumps(out_dict, default=str))
            
            if partner_id:
                partner_name = self.content.get_user_info(partner_id)['name']

                partner_prerequisite_assignments_not_completed = await self.get_prerequisite_assignments_not_completed(course_id, assignment_details, partner_id)

                if len(partner_prerequisite_assignments_not_completed) > 0:
                    out_dict["message"] = f"ineligible: Your pair-programming partner ({partner_name}) has NOT completed the prerequisite assignment(s) for this assignment, so you may not submit a solution with this partner. Your submission has NOT been saved."

                    return self.write(json.dumps(out_dict, default=str))

            out_dict = await exec_code(self.settings_dict, code, exercise_details["verification_code"], exercise_details, True)

            if out_dict["message"] == "":
                out_dict["all_passed"] = check_test_outputs(exercise_details, out_dict["test_outputs"])

                out_dict["score"] = self.calc_exercise_score(assignment_details, out_dict["all_passed"])

                out_dict["submission_id"] = await self.content.save_submission(course_id, assignment_id, exercise_id, user_id, code, out_dict["all_passed"], date, exercise_details, out_dict["test_outputs"], out_dict["score"], partner_id)

                if partner_id:
                    out_dict["partner_name"] = partner_name

                    await self.content.save_submission(course_id, assignment_id, exercise_id, partner_id, code, out_dict["all_passed"], date, exercise_details, out_dict["test_outputs"], out_dict["score"], user_id)

                sanitize_test_outputs(exercise_details, out_dict["test_outputs"])
        except ConnectionError as inst:
            out_dict["message"] = "error: The front-end server was unable to contact the back-end server."
            out_dict["all_passed"] = False
        except ReadTimeout as inst:
            out_dict["message"] = f"error: Your solution timed out after {self.settings_dict['back_ends'][exercise_details['back_end']]['timeout_seconds']} seconds."
            out_dict["all_passed"] = False
        except Exception as inst:
            out_dict["message"] = f"error: {format_output_as_html(traceback.format_exc())}"
            out_dict["all_passed"] = False

        self.write(json.dumps(out_dict, default=str))

    def calc_exercise_score(self, assignment_details, passed):
        if passed:
            if assignment_details["due_date"] and assignment_details["due_date"] < datetime.utcnow():
                if assignment_details["allow_late"]:
                    return 100 * assignment_details["late_percent"]
            else:
                return 100
        else:
            return 0