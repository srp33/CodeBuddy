# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class ViewInstructorSolutionHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id, exercise_id):
        try:
            #client_ip = get_client_ip_address(self.request)
            user_info = self.user_info

            course_basics = await self.get_course_basics(course_id)
            assignment_statuses = await self.get_assignment_statuses(course_basics)
            course_details = await self.get_course_details(course_id)

            assignment_basics = await self.get_assignment_basics(course_basics, assignment_id)
            exercise_basics = await self.get_exercise_basics(course_basics, assignment_basics, exercise_id)

            assignment_details = await self.get_assignment_details(course_basics, assignment_id)
            exercise_details = await self.get_exercise_details(course_basics, assignment_basics, exercise_id)

            instructor_solution = exercise_details["solution_code"]

            # if exercise_details["back_end"] == "multiple_choice":
            #     instructor_solution = "<br>".join([key for key, value in ujson.loads(instructor_solution).items() if value])

            exercise_statuses = self.content.get_exercise_statuses(course_id, assignment_id, user_info["user_id"])

            user_code = self.content.get_most_recent_submission_code(course_id, assignment_id, exercise_id, user_info["user_id"], exercise_details["back_end"] != "multiple_choice")

            should_show = await self.check_whether_should_show_exercise(course_id, assignment_id, assignment_details, assignment_statuses, self.courses, assignment_basics, course_basics)

            if should_show:
                next_prev_exercises = self.content.get_next_prev_exercises(course_id, assignment_id, exercise_id, exercise_statuses)
                thumb_status = await self.content.get_thumb_status(course_id, assignment_id, exercise_id, user_info["user_id"], "instructor_solution")

                format_exercise_details(exercise_details, course_basics, assignment_basics, user_info, self.content)
                self.render("view_instructor_solution.html", courses=self.courses, assignment_statuses=assignment_statuses, course_basics=course_basics, assignment_basics=assignment_basics, assignment_details=assignment_details, exercise_basics=exercise_basics, exercise_details=exercise_details, exercise_statuses=exercise_statuses, instructor_solution=instructor_solution, next_exercise=next_prev_exercises["next"],prev_exercise=next_prev_exercises["previous"], thumb_status=thumb_status, user_code=user_code, user_info=user_info, check_for_restrict_other_assignments=course_details["check_for_restrict_other_assignments"], is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_assistant=await self.is_assistant_for_course(course_id), support_questions=False)
        except Exception as inst:
            render_error(self, traceback.format_exc())