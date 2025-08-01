# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class EditExerciseHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id, exercise_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)
                assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)
                exercise_basics = self.content.get_exercise_basics(course_basics, assignment_basics, exercise_id)
                
                exercise_details = await self.get_exercise_details(course_basics, assignment_basics, exercise_id)

                if exercise_details["back_end"] == "multiple_choice":
                    return self.redirect(f"/edit_mc_exercise/{course_id}/{assignment_id}/{exercise_id}")

                exercise_statuses = self.content.get_exercise_statuses(course_id, assignment_id, self.get_current_user(), show_hidden=True)

                for test_title in exercise_details["tests"]:
                    exercise_details["tests"][test_title]["txt_output"] = exercise_details["tests"][test_title]["txt_output"]
                    exercise_details["tests"][test_title]["txt_output_formatted"] = format_output_as_html(exercise_details["tests"][test_title]["txt_output"])

                next_prev_exercises = self.content.get_next_prev_exercises(course_id, assignment_id, exercise_id, exercise_statuses)

                back_ends = get_back_ends_dict(self.in_production_mode())

                self.render("edit_exercise.html", courses=self.courses, assignment_statuses=await self.get_assignment_statuses(course_basics), exercise_statuses=exercise_statuses, course_basics=course_basics, assignment_basics=assignment_basics, exercise_basics=exercise_basics, exercise_basics_json=escape_json_string(json.dumps(exercise_basics, default=str)), exercise_details_json=escape_json_string(json.dumps(exercise_details, default=str)), next_exercise=next_prev_exercises["next"], prev_exercise=next_prev_exercises["previous"], back_ends_json=escape_json_string(json.dumps(back_ends, default=str)), user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_assistant=await self.is_assistant_for_course(course_id), is_edit_page=True)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def post(self, course_id, assignment_id, exercise_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)
                assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)

                exercise_details = ujson.loads(self.request.body)

                exercise_basics = self.content.get_exercise_basics(course_basics, assignment_basics, exercise_id)
                exercise_basics["title"] = exercise_details.pop("title")
                exercise_basics["visible"] = exercise_details.pop("visible")

                # Make sure an exercise with this title does not already exist.
                existing_exercise_titles = [x[1]["title"] for x in self.content.get_exercises(course_basics, assignment_basics, show_hidden=True) if x[0] != exercise_basics["id"]]

                if exercise_basics["title"] in existing_exercise_titles:
                    return self.write_post_output(None, "Error: An exercise with that title already exists.", None)

                current_time = get_current_datetime()
                if exercise_basics["exists"]:
                    exercise_details["date_created"] = (await self.get_exercise_details(course_basics, assignment_basics, exercise_id))["date_created"]
                else:
                     exercise_details["date_created"] = current_time

                exercise_details["date_updated"] = current_time

                result, success = await execute_and_save_exercise(self.settings_dict, self.content, exercise_basics, exercise_details)

                if success:
                    return self.write_post_output(result, "", exercise_details)
                else:
                    return self.write_post_output(None, result, None)
            else:
                return self.write_post_output(None, "Error: You do not have permission to edit exercises for this course.", None)
        except ConnectionError as inst:
            return self.write_post_output(None, "Error: The front-end server was unable to contact the back-end server.", None)
            print(traceback.format_exc())
        except ReadTimeout as inst:
            return self.write_post_output(None, "Error: Your solution timed out when attempting to contact the back-end server.", None)
        except Exception as inst:
            return self.write_post_output(None, f"Error: {traceback.format_exc()}", None)

    def write_post_output(self, exercise_id, message, exercise_details):
        try:
            self.write(json.dumps({"exercise_id": exercise_id, "message": message, "exercise_details": exercise_details}, default=str))
        except:
            self.write(json.dumps({"exercise_id": None, "message": traceback.format_exc(), "exercise_details": None}, default=str))