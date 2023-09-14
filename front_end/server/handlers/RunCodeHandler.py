# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class RunCodeHandler(BaseUserHandler):
    async def post(self, course_id, assignment_id, exercise_id):
        out_dict = {"message": "", "test_outputs": {}, "all_passed": False}

        try:
            code = self.get_body_argument("user_code").replace("\r", "")

            course_basics = await self.get_course_basics(course_id)
            assignment_basics = await self.get_assignment_basics(course_basics, assignment_id)
            exercise_details = await self.get_exercise_details(course_basics, assignment_basics, exercise_id)

            single_test = self.get_query_argument('test', None)
            if single_test is not None and single_test in exercise_details["tests"]:
                exercise_details["tests"] = {single_test: exercise_details["tests"][single_test]}

            out_dict = await exec_code(self.settings_dict, code, exercise_details["verification_code"], exercise_details, True)

            if out_dict["message"] == "":
                out_dict["all_passed"] = check_test_outputs(exercise_details, out_dict["test_outputs"])

                sanitize_test_outputs(exercise_details, out_dict["test_outputs"])
        except ConnectionError as inst:
            out_dict["message"] = "The front-end server was unable to contact the back-end server."
        except ReadTimeout as inst:
            out_dict["message"] = f"Your solution timed out after {self.settings_dict['back_ends'][exercise_details['back_end']]['timeout_seconds']} seconds."
        except Exception as inst:
            out_dict["message"] = format_output_as_html(traceback.format_exc())

        self.write(json.dumps(out_dict, default=str))