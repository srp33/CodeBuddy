# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class StudentExerciseHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id, exercise_id, student_id):
        try:
            is_assistant = await self.is_assistant_for_course(course_id)

            if self.is_administrator or await self.is_instructor_for_course(course_id) or is_assistant:
                course_basics = await self.get_course_basics(course_id)
                assignment_statuses = await self.get_assignment_statuses(course_basics)
                assignment_basics = await self.get_assignment_basics(course_basics, assignment_id)
                exercise_basics = await self.get_exercise_basics(course_basics, assignment_basics, exercise_id)

                assignment_details = await self.get_assignment_details(course_basics, assignment_id)
                exercise_details = await self.get_exercise_details(course_basics, assignment_basics, exercise_id)

                presubmission, submissions, has_passed = self.content.get_submissions(course_id, assignment_id, exercise_id, student_id, exercise_details)
                num_submissions = len(submissions)

                code_completion_path = None
                back_end_description = None
                if exercise_details["back_end"] != "multiple_choice":
                    back_end_config = get_back_end_config(exercise_details["back_end"])
                    code_completion_path = back_end_config["code_completion_path"]
                    back_end_description = back_end_config["description"]

                student_info = self.content.get_user_info(student_id)
                score = self.content.get_student_exercise_score(course_id, assignment_id, exercise_id, student_id)

                exercise_statuses = self.content.get_exercise_statuses(course_id, assignment_id, self.get_current_user(), show_hidden=False)
                
                next_prev_exercises = self.content.get_next_prev_exercises(course_id, assignment_id, exercise_id, exercise_statuses)

                format_exercise_details(exercise_details, course_basics, assignment_basics, student_info, self.content, next_prev_exercises, format_data=True)

                args = {"student_info": student_info, "student_id": student_id, "score": score, "courses": self.courses, "course_basics": course_basics, "assignment_statuses": assignment_statuses, "assignment_basics": assignment_basics, "exercise_basics": exercise_basics, "assignment_details": assignment_details, "exercise_details": exercise_details, "tests": exercise_details["tests"], "presubmission": presubmission, "code_completion_path": code_completion_path, "back_end_description": back_end_description, "submissions": submissions, "exercise_statuses": exercise_statuses, "next_prev_exercises": next_prev_exercises, "num_submissions": num_submissions, "user_info": self.user_info, "user_id": self.get_current_user(), "next_prev_student_ids": self.content.get_next_prev_student_ids(course_id, student_id), "check_for_restrict_other_assignments": False, "is_administrator": self.is_administrator, "is_instructor": await self.is_instructor_for_course(course_id), "is_assistant": is_assistant}

                if exercise_details["back_end"] == "multiple_choice":
                    solutions_dict = json.loads(exercise_details["solution_code"])

                    answer_options = [(answer_option, is_correct) for answer_option, is_correct in sorted(solutions_dict.items())]
                    args["answer_options"] = answer_options

                    if presubmission and "sandbox_code:" in presubmission:
                        args["presubmission"] = presubmission.split("sandbox_code:")[1]
                    else:
                        args["presubmission"] = ""

                    self.render("mc_student_exercise.html", **args)
                else:
                    if has_passed:
                        args["presubmission"] = ""

                    self.render("student_exercise.html", **args)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())