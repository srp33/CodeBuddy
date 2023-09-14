# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class GetPartnerIDHandler(BaseUserHandler):
    async def get(self, course_id, partner_name):
        partner_dict = await self.get_partner_info(course_id, True)

        # Determines whether the partner_key is a valid one while hiding student emails from the client side.
        if partner_name in partner_dict:
            self.write(json.dumps(partner_dict[partner_name], default=str))
        else:
            self.write(json.dumps({"error": "Invalid partner key"}, default=str))