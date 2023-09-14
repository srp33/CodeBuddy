# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class UnavailableExerciseHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id):
        try:
            course_basics = await self.get_course_basics(course_id)

            return self.render("unavailable_exercise.html", courses=self.courses, assignments=await self.get_assignments(course_basics), course_basics=course_basics, assignment_basics=await self.get_assignment_basics(course_basics, assignment_id), user_info=self.user_info, is_administrator=self.is_administrator)
        except Exception as inst:
            render_error(self, traceback.format_exc())