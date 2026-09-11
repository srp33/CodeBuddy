# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class RedeemSecureAssignmentHandler(BaseUserHandler):
    async def get(self, code):
        try:
            code = (code or "").strip().upper()
            assignment_row = self.content.get_assignment_by_secure_access_code(code)

            if not assignment_row:
                return self.render(
                    "error.html",
                    error_title="Invalid secure access link",
                    error_message="This secure access link is not valid. Please ask your instructor for an updated QR code or link.",
                )

            course_id = str(assignment_row["course_id"])
            assignment_id = str(assignment_row["assignment_id"])
            user_id = self.get_current_user()

            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                return self.redirect(f"/assignment/{course_id}/{assignment_id}")

            registered_ids = [row[0] for row in self.content.get_registered_students(course_id)]
            if user_id not in registered_ids:
                return self.render(
                    "error.html",
                    error_title="Course access required",
                    error_message="You must be logged in and registered for this course before you can unlock a secured assignment. Please register for the course, then scan the QR code or open the secure link again.",
                )

            self.content.authorize_secure_assignment_access(course_id, assignment_id, user_id)
            return self.redirect(f"/assignment/{course_id}/{assignment_id}")
        except Exception:
            render_error(self, traceback.format_exc())
