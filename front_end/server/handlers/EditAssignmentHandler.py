# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class EditAssignmentHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)
                course_details = await self.get_course_details(course_id)
                assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)
                assignment_details = self.content.get_assignment_details(course_basics, assignment_id)

                assignment_statuses = await self.get_assignment_statuses(course_basics)
                assignment_groups = self.content.get_assignment_groups(course_id)

                assignment_ids_prerequiring = self.content.get_assignments_prerequiring_this_assignment(course_id, assignment_id)

                prerequisite_assignment_options = []
                for assignment in assignment_statuses:
                    assignment_id = assignment[0]
                    title = assignment[2]["title"]
                    visible = assignment[2]["visible"]

                    if visible == True and assignment_id != assignment_basics["id"] and assignment_id not in assignment_ids_prerequiring:
                        prerequisite_assignment_options.append((assignment_id, title))

                self.render("edit_assignment.html", courses=self.courses, assignment_statuses=assignment_statuses, assignment_groups=assignment_groups, course_basics=course_basics, course_details=course_details, assignment_basics=assignment_basics, assignment_basics_json=escape_json_string(json.dumps(assignment_basics)), assignment_details_json=escape_json_string(json.dumps(assignment_details, default=str)), prerequisite_assignment_options=escape_json_string(json.dumps(prerequisite_assignment_options)), all_students=escape_json_string(json.dumps(self.content.get_registered_students(course_id))), user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_assistant=await self.is_assistant_for_course(course_id), is_edit_page=True)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def post(self, course_id, assignment_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)
                assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)

                assignment_details = ujson.loads(self.request.body)

                assignment_basics["title"] = assignment_details.pop("title")
                assignment_basics["visible"] = assignment_details.pop("visible")

                if assignment_details["start_date"]:
                    assignment_details["start_date"] = datetime.strptime(assignment_details["start_date"], "%a, %d %b %Y %H:%M:%S %Z")

                if assignment_details["due_date"]:
                    assignment_details["due_date"] = datetime.strptime(assignment_details["due_date"], "%a, %d %b %Y %H:%M:%S %Z")

                current_time = get_current_datetime()

                if assignment_basics["exists"]:
                    assignment_details["date_created"] = (await self.get_assignment_details(course_basics, assignment_basics["id"]))["date_created"]
                else:
                    assignment_details["date_created"] = current_time
                assignment_details["date_updated"] = current_time

                # Make sure an assignment with this title doesn't already exist.
                existing_assignment_titles = [x[2]["title"] for x in self.content.get_assignments(course_basics, show_hidden=True) if x[0] != assignment_basics["id"]]
                if assignment_basics["title"] in existing_assignment_titles:
                    return self.write_post_output(None, "Error: An assignment with that title already exists.", None)

                assignment_id = self.content.save_assignment(assignment_basics, assignment_details)

                return self.write_post_output(assignment_id, "", assignment_details)
            else:
                return self.write_post_output(None, "Error: You do not have permission to edit assignments for this course.", None)
        except Exception as inst:
            return self.write_post_output(None, f"Error: {traceback.format_exc()}", None)

    def write_post_output(self, assignment_id, message, assignment_details):
        try:
            self.write(json.dumps({"assignment_id": assignment_id, "message": message, "assignment_details": assignment_details}, default=str))
        except:
            self.write(json.dumps({"assignment_id": None, "message": traceback.format_exc(), "assignment_details": None}, default=str))