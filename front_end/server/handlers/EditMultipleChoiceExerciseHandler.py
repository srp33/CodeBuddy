# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class EditMultipleChoiceExerciseHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id, exercise_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)
                assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)
                exercise_basics = self.content.get_exercise_basics(course_basics, assignment_basics, exercise_id)
                
                exercise_details = await self.get_exercise_details(course_basics, assignment_basics, exercise_id)

                exercise_statuses = self.content.get_exercise_statuses(course_id, assignment_id, self.get_current_user(), show_hidden=True)

                next_prev_exercises = self.content.get_next_prev_exercises(course_id, assignment_id, exercise_id, exercise_statuses)

                self.render("edit_mc_exercise.html", courses=self.courses, assignment_statuses=await self.get_assignment_statuses(course_basics), exercise_statuses=exercise_statuses, course_basics=course_basics, assignment_basics=assignment_basics, exercise_basics=exercise_basics, exercise_basics_json=escape_json_string(json.dumps(exercise_basics, default=str)), exercise_details_json=escape_json_string(json.dumps(exercise_details, default=str)), next_exercise=next_prev_exercises["next"], prev_exercise=next_prev_exercises["previous"], user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_assistant=await self.is_assistant_for_course(course_id))
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def post(self, course_id, assignment_id, exercise_id):
        results = {"exercise_id": None, "message": "", "exercise_details": None}        

        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)
                assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)
                exercise_basics = self.content.get_exercise_basics(course_basics, assignment_basics, exercise_id)
                exercise_details = await self.get_exercise_details(course_basics, assignment_basics, exercise_id)

                submission_dict = ujson.loads(self.request.body)

                exercise_basics["title"] = submission_dict.pop("title")
                exercise_basics["visible"] = submission_dict.pop("visible")

                exercise_details["back_end"] = "multiple_choice"
                for key, value in submission_dict.items():
                    if key != "title" and key != "visible":
                        exercise_details[key] = value

                current_time = get_current_datetime()
                if not exercise_basics["exists"]:
                    exercise_details["date_created"] = current_time
                exercise_details["date_updated"] = current_time

                exercise_id = self.content.save_exercise(exercise_basics, exercise_details)

                results["exercise_id"] = exercise_id
                results["exercise_details"] = exercise_details
            else:
                results["message"] = "You do not have permission to edit exercises for this course."
        except ConnectionError as inst:
            results["message"] = "The front-end server was unable to contact the back-end server."
            print(traceback.format_exc())
        except Exception as inst:
            results["message"] = traceback.format_exc()

        try:
            self.write(json.dumps(results, default=str))
        except:
            results = {"exercise_id": None, "message": traceback.format_exc(), "exercise_details": None}
            self.write(json.dumps(results, default=str))