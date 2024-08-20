# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class RunCodeSandboxHandler(BaseUserHandler):
    async def post(self, course_id, assignment_id, exercise_id, sandbox_back_end):
        out_dict = {"message": "", "txt_output": {}}

        try:
            course_basics = await self.get_course_basics(course_id)
            assignment_basics = await self.get_assignment_basics(course_basics, assignment_id)
            exercise_details = await self.get_exercise_details(course_basics, assignment_basics, exercise_id)

            exercise_details["back_end"] = sandbox_back_end

            exercise_details["tests"]["Test"] = {"test_id": 0, "before_code": "", "after_code": "", "instructions": "", "can_see_test_code": True, "can_see_expected_output": True, "can_see_code_output": True, "txt_output": "", "jpg_output": ""}

            user_code = self.get_body_argument("user_code").replace("\r", "")

            result_dict = await exec_code(self.settings_dict, user_code, "", exercise_details, True)

            out_dict["txt_output"] = result_dict["test_outputs"]["Test"]["txt_output_formatted"]
        except ConnectionError as inst:
            out_dict["message"] = "The front-end server was unable to contact the back-end server."
        except ReadTimeout as inst:
            out_dict["message"] = f"Your solution timed out after {self.settings_dict['back_ends'][exercise_details['back_end']]['timeout_seconds']} seconds."
        except Exception as inst:
            out_dict["message"] = traceback.format_exc()

        self.write(json.dumps(out_dict, default=str))