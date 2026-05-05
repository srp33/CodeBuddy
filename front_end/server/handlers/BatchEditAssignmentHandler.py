# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class BatchEditAssignmentHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)
                assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)
                assignment_statuses = await self.get_assignment_statuses(course_basics)

                exercise_statuses = self.content.get_exercise_statuses(course_id, assignment_id, None, show_hidden=False)
                bulk_data = self.content.get_exercise_bulk_edit_data(course_id, assignment_id)

                visible_exercises = []
                for exercise_id, status in exercise_statuses:
                    ex_data = bulk_data.get(exercise_id, {})
                    visible_exercises.append({
                        "id": exercise_id,
                        "title": status["title"],
                        "enable_pair_programming": bool(status["enable_pair_programming"]),
                        "weight": status["weight"],
                        "min_solution_length": ex_data.get("min_solution_length", 1),
                        "max_solution_length": ex_data.get("max_solution_length", 10000),
                        "max_submissions": ex_data.get("max_submissions", 0),
                    })

                self.render("batch_edit_assignment.html", courses=self.courses, assignment_statuses=assignment_statuses, course_basics=course_basics, assignment_basics=assignment_basics, visible_exercises=visible_exercises, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_assistant=await self.is_assistant_for_course(course_id))
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def post(self, course_id, assignment_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)
                assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)

                body = ujson.loads(self.request.body)
                field = body["field"]
                updates = body["updates"]

                valid_fields = {"title", "pair_programming", "weight", "min_length", "max_length", "max_submissions"}
                if field not in valid_fields:
                    return self.write(json.dumps({"message": f"Error: Invalid field '{field}'."}))

                existing_exercises = self.content.get_exercises(course_basics, assignment_basics, show_hidden=True)

                errors = []
                validated_updates = []

                for update in updates:
                    exercise_id = update["exercise_id"]
                    value = update["value"]

                    if field == "title":
                        value = value.strip()
                        if not value:
                            errors.append(f"A title cannot be empty.")
                            continue
                        if len(value) > 100:
                            errors.append(f"Title '{value[:50]}...' exceeds 100 characters.")
                            continue
                        other_titles = [x[1]["title"] for x in existing_exercises if x[0] != exercise_id]
                        if value in other_titles:
                            errors.append(f"An exercise with the title '{value}' already exists.")
                            continue
                        for ex in existing_exercises:
                            if ex[0] == exercise_id:
                                ex[1]["title"] = value
                                break

                    elif field == "pair_programming":
                        value = True if value == "Yes" else False

                    elif field == "weight":
                        try:
                            value = float(value)
                            if value <= 0:
                                errors.append(f"Weight must be a positive number.")
                                continue
                        except (ValueError, TypeError):
                            errors.append(f"Invalid weight value.")
                            continue

                    elif field in ("min_length", "max_length"):
                        try:
                            value = int(value)
                            if value < 1:
                                errors.append(f"Response length must be at least 1.")
                                continue
                            if value > 10000:
                                errors.append(f"Response length cannot exceed 10000.")
                                continue
                            row = self.content.fetchone(
                                "SELECT min_solution_length, max_solution_length FROM exercises WHERE course_id=? AND assignment_id=? AND exercise_id=?",
                                (course_id, assignment_id, exercise_id))
                            if row:
                                if field == "max_length" and value < row["min_solution_length"]:
                                    errors.append(f"Maximum response length cannot be less than the minimum response length.")
                                    continue
                                if field == "min_length" and value > row["max_solution_length"]:
                                    errors.append(f"Minimum response length cannot be greater than the maximum response length.")
                                    continue
                        except (ValueError, TypeError):
                            errors.append(f"Invalid response length value.")
                            continue

                    elif field == "max_submissions":
                        try:
                            value = int(value)
                            if value not in [0, 1, 2, 3, 4, 5, 10, 20, 50, 100]:
                                errors.append(f"Invalid value for maximum submissions.")
                                continue
                        except (ValueError, TypeError):
                            errors.append(f"Invalid value for maximum submissions.")
                            continue

                    validated_updates.append({"exercise_id": exercise_id, "value": value})

                if errors:
                    return self.write(json.dumps({"message": "\n".join(errors)}))

                for update in validated_updates:
                    self.content.update_exercise_field(course_id, assignment_id, update["exercise_id"], field, update["value"])

                return self.write(json.dumps({"message": ""}))
            else:
                return self.write(json.dumps({"message": "Error: You do not have permission to edit exercises for this course."}))
        except Exception as inst:
            return self.write(json.dumps({"message": f"Error: {traceback.format_exc()}"}))
