# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class VerifySecurityCodeHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id):
        try:
            course_basics = await self.get_course_basics(course_id)
            assignment_basics = await self.get_assignment_basics(course_basics, assignment_id)
            assignment_statuses = await self.get_assignment_statuses(course_basics)

            self.render("verify_security_code.html", courses=self.courses, course_basics=course_basics, assignment_basics=assignment_basics, assignment_statuses=assignment_statuses, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_assistant=await self.is_assistant_for_course(course_id))
        except:
            render_error(self, traceback.format_exc())

    async def post(self, course_id, assignment_id):
        try:
            security_code = self.request.body.decode()

            verification_status = self.content.verify_security_code(course_id, assignment_id, security_code, self.get_current_user())

            if verification_status == -1:
                status = "previously_verified"
            elif verification_status is False:
                status = "could_not_verify"
            else:
                status = "verified"
        except:
            status = traceback.format_exc()

        self.write(status)