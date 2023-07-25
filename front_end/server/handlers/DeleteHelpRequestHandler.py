# <copyright_statement>
#   CodeBuddy - A learning management system for computer programming
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class DeleteHelpRequestHandler(BaseUserHandler):
    async def post(self, course_id, assignment_id, exercise_id, user_id):
        try:
            course_basics = await self.get_course_basics(course_id)

            self.content.delete_help_request(course_id, assignment_id, exercise_id, user_id)
            self.render("help_requests.html", courses=self.courses, course_basics=course_basics, assignments=self.content.get_assignments(course_basics), help_requests=self.content.get_help_requests(course_id), user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_assistant=await self.is_assistant_for_course(course_id))
        except Exception as inst:
            render_error(self, traceback.format_exc())