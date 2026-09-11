# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class SecureAssignmentHandler(BaseUserHandler):
    def get_secure_access_url(self, code):
        if self.in_production_mode():
            base_url = f"https://{self.settings_dict['domain']}"
        else:
            base_url = f"{self.request.protocol}://{self.request.host}"
        return f"{base_url}/s/{code}"

    async def post(self, course_id, assignment_id):
        try:
            if not (self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id)):
                return self.write(json.dumps({"message": "Error: You do not have permission to secure this assignment."}))

            course_basics = await self.get_course_basics(course_id)
            assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)
            if not assignment_basics["exists"]:
                return self.write(json.dumps({"message": "Error: Please save the assignment before securing it."}))

            body = ujson.loads(self.request.body) if self.request.body else {}
            action = body.get("action", "enable")

            if action == "disable":
                self.content.disable_assignment_secure_access(course_id, assignment_id)
                return self.write(json.dumps({"message": "", "secure_access_code": None, "secure_access_url": None}))

            code = self.content.enable_assignment_secure_access(course_id, assignment_id)
            return self.write(json.dumps({
                "message": "",
                "secure_access_code": code,
                "secure_access_url": self.get_secure_access_url(code),
            }))
        except Exception:
            return self.write(json.dumps({"message": f"Error: {traceback.format_exc()}"}))
