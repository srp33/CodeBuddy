# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class ResaveExercisesHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)
                assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)
                exercises = self.content.get_exercises(course_basics, assignment_basics)

                output = f"<h4>Re-saving exercises for {course_basics['title']} and {assignment_basics['title']}</h4>"

                an_error_occurred = False

                for exercise in exercises:
                    exercise_basics = self.content.get_exercise_basics(course_basics, assignment_basics, exercise[0])
                    exercise_details = await self.get_exercise_details(course_basics, assignment_basics, exercise[0])

                    output += f"<p>Working on {exercise_basics['title']} (ID: {exercise_basics['id']})..."

                    if exercise_details["back_end"] == "multiple_choice":
                        output += "not necessary to re-save because it is a multiple-choice question.</p>"
                    else:
                        exercise_details["date_updated"] = get_current_datetime()

                        try:
                            result, success = await execute_and_save_exercise(self.settings_dict, self.content, exercise_basics, exercise_details)
                        except ConnectionError as inst:
                            result = "The front-end server was unable to contact the back-end server."
                            success = False
                        except ReadTimeout as inst:
                            result = "Code execution timed out."
                            success = False
                        except Exception as int:
                            result = traceback.format_exc()
                            success = False

                        if success:
                            output += f"success!</p>"
                        else:
                            output += f"<strong><font color='red'>error occurred: {result}</font></strong></p>"
                            an_error_occurred = True

                if an_error_occurred:
                    output += "<h4>An error occurred for at least one of the exercises.</h4>"
                else:
                    output += "<h4>All done.</h4>"

                self.render("resave_exercises.html", courses=self.courses, assignment_statuses=await self.get_assignment_statuses(course_basics), course_basics=course_basics, assignment_basics=assignment_basics, output=output, user_info=self.user_info, is_administrator=self.is_administrator)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())