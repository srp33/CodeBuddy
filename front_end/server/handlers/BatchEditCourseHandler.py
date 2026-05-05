# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class BatchEditCourseHandler(BaseUserHandler):
    async def get(self, course_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)
                all_assignments_raw = self.content.get_assignments(course_basics, show_hidden=True)
                bulk_data = self.content.get_assignment_bulk_edit_data(course_id)

                all_assignments = []
                for assignment_id, _, assignment in all_assignments_raw:
                    extra = bulk_data.get(assignment_id, {})
                    all_assignments.append({
                        "id": assignment_id,
                        "title": assignment["title"],
                        "start_date": assignment["start_date"],
                        "due_date": assignment["due_date"],
                        "has_timer": bool(extra.get("has_timer", False)),
                        "allow_students_view_submissions": bool(extra.get("allow_students_view_submissions", False)),
                        "require_security_codes": extra.get("require_security_codes", 0),
                        "show_run_button": extra.get("show_run_button", True),
                        "support_questions": extra.get("support_questions", False),
                    })

                self.render("batch_edit_course.html", courses=self.courses, course_basics=course_basics, all_assignments=all_assignments, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_assistant=await self.is_assistant_for_course(course_id))
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def post(self, course_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)
                body = ujson.loads(self.request.body)
                field = body["field"]
                updates = body["updates"]

                valid_fields = {"title", "dates", "allow_students_view_submissions", "require_security_codes", "show_run_button", "support_questions"}
                if field not in valid_fields:
                    return self.write(json.dumps({"message": f"Error: Invalid field '{field}'."}))

                existing_assignments = self.content.get_assignments(course_basics, show_hidden=True)

                errors = []
                validated_updates = []

                for update in updates:
                    assignment_id = update["assignment_id"]
                    value = update["value"]

                    if field == "title":
                        value = value.strip()
                        if not value:
                            errors.append("A title cannot be empty.")
                            continue
                        if len(value) > 100:
                            errors.append(f"Title '{value[:50]}...' exceeds 100 characters.")
                            continue
                        other_titles = [x[2]["title"] for x in existing_assignments if x[0] != assignment_id]
                        if value in other_titles:
                            errors.append(f"An assignment with the title '{value}' already exists.")
                            continue
                        for asgn in existing_assignments:
                            if asgn[0] == assignment_id:
                                asgn[2]["title"] = value
                                break

                    elif field == "dates":
                        try:
                            parsed = ujson.loads(value)
                            start_val = parsed.get("start_date", "")
                            due_val = parsed.get("due_date", "")
                            start_date = None
                            due_date = None
                            if start_val:
                                start_date = datetime.strptime(start_val, "%a, %d %b %Y %H:%M:%S %Z")
                            if due_val:
                                due_date = datetime.strptime(due_val, "%a, %d %b %Y %H:%M:%S %Z")
                            if start_date and due_date and due_date <= start_date:
                                asgn_title = next((x[2]["title"] for x in existing_assignments if x[0] == assignment_id), f"ID {assignment_id}")
                                errors.append(f"The due date must be later than the start date for \"{asgn_title}\".")
                                continue
                            value = {"start_date": start_date, "due_date": due_date}
                        except (ValueError, TypeError) as e:
                            errors.append(f"Invalid date value: {e}")
                            continue

                    elif field == "require_security_codes":
                        try:
                            value = int(value)
                            if value not in [0, 1, 2]:
                                errors.append("Invalid value for require security codes.")
                                continue
                        except (ValueError, TypeError):
                            errors.append("Invalid value for require security codes.")
                            continue

                    elif field in ("allow_students_view_submissions", "show_run_button", "support_questions"):
                        value = True if value == "Yes" else False

                    validated_updates.append({"assignment_id": assignment_id, "value": value})

                if errors:
                    return self.write(json.dumps({"message": "\n".join(errors)}))

                for update in validated_updates:
                    self.content.update_assignment_field(course_id, update["assignment_id"], field, update["value"])

                return self.write(json.dumps({"message": ""}))
            else:
                return self.write(json.dumps({"message": "Error: You do not have permission to edit assignments for this course."}))
        except Exception as inst:
            return self.write(json.dumps({"message": f"Error: {traceback.format_exc()}"}))
