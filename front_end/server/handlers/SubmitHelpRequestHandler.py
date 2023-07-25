# <copyright_statement>
#   CodeBuddy - A learning management system for computer programming
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *
import datetime as dt

class SubmitHelpRequestHandler(BaseUserHandler):
    async def post(self, course_id, assignment_id, exercise_id):
        try:
            user_id = self.get_current_user()
            student_comment = self.get_body_argument("student_comment")
            help_request = self.content.get_help_request(course_id, assignment_id, exercise_id, user_id)
            if help_request:
                self.content.update_help_request(course_id, assignment_id, exercise_id, user_id, student_comment)

            else:
                code = self.get_body_argument("user_code").replace("\r", "")

                course_basics = await self.get_course_basics(course_id)
                assignment_basics = await self.get_assignment_basics(course_basics, assignment_id)

                # exercise_basics = self.get_exercise_basics(course_basics, assignment_basics, exercise)
                exercise_details = await self.get_exercise_details(course_basics, assignment_basics, exercise_id)

                text_output, jpg_output, tests = await exec_code(self.settings_dict, code, exercise_details, request=None)
                text_output = format_output_as_html(text_output)

                self.content.save_help_request(course_id, assignment_id, exercise_id, user_id, code, text_output, jpg_output, student_comment, dt.datetime.utcnow())

        except Exception as inst:
            render_error(self, traceback.format_exc())