# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class IsTakingRestrictedAssignmentHandler(BaseUserHandler):
    async def get(self, user_id, assignment_id):
        try:
            __, is_taking_restricted_assignment = self.content.is_taking_timed_assignment(user_id, assignment_id)

            self.write(json.dumps(is_taking_restricted_assignment, default=str))
        except Exception as inst:
            self.write(json.dumps(traceback.format_exc(), default=str))