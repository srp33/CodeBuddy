# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class AnswerQuestionHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id, exercise_id, question_id):
        try:
            if self.is_administrator or self.is_instructor_for_course(course_id) or self.is_assistant_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)
                assignment_basics = await self.get_assignment_basics(course_basics, assignment_id)
                exercise_basics = await self.get_exercise_basics(course_basics, assignment_basics, exercise_id)
                exercise_details = await self.get_exercise_details(course_basics, assignment_basics, exercise_id)
                assignment_statuses = await self.get_assignment_statuses(course_basics)

                question = self.content.get_question(question_id)

                if question:
                    questioner_info = self.content.get_user_info(question["questioner_id"])
                    answerer_info = self.content.get_user_info(question["answerer_id"])

                    self.render("answer_question.html", courses=self.courses, assignment_statuses=assignment_statuses,course_basics=course_basics, assignment_basics=assignment_basics, exercise_basics=exercise_basics, exercise_details=exercise_details, user_info=self.user_info, is_administrator=self.is_administrator, question=question, questioner_info=questioner_info, answerer_info=answerer_info, question_id=question_id)
                else:
                    self.render("unavailable_question.html", courses=self.courses, user_info=self.user_info, is_administrator=self.is_administrator)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def post(self, course_id, assignment_id, exercise_id, question_id):
        try:
            course_basics = await self.get_course_basics(course_id)
            assignment_basics = await self.get_assignment_basics(course_basics, assignment_id)
            exercise_basics = await self.get_exercise_basics(course_basics, assignment_basics, exercise_id)

            question = self.get_body_argument("question")
            question_info = self.content.get_question(question_id)
            questioner_id = question_info["questioner_id"]
            questioner_info = self.content.get_user_info(questioner_id)
            question_modified = question != question_info["question"]
            answerer_id = self.current_user
            answerer_info = self.content.get_user_info(answerer_id)
            answer = self.get_body_argument("answer")
            answer_modified = answer != question_info["answer"]
            answerer_share = self.get_body_argument("answerer_share") == "true"

            self.content.answer_question(question_id, question, question_modified, answerer_id, answer, answerer_share)

            exercise_url = f"https://{self.settings_dict['domain']}/exercise/{course_id}/{assignment_id}/{exercise_id}"

            message = f"<p>Your question has been answered.</p><p>Your question"

            if question_modified:
                message += " (has been modified)"
            
            message += f":</p><p><pre>{question}</pre></p><p>Answer (by {answerer_info['name']}"

            if answer_modified:
                message += ", previous answer was modified"
            
            message += f"):</p><p><pre>{answer}</pre></p>"
            
            if answerer_share:
                message += f"<p>This answer has been posted for other students to see. Click on the \"Q & A\" button at {exercise_url}.</p>"
            else:
                message += f"<p>This answer has NOT been posted for other students to see.</p>"

            message += f"<p>Please do not reply directly to this email. Instead contact the instructor or a teaching assistant, if needed.</p>"

            smtp_server = self.settings_dict["smtp_server"]
            smtp_port = int(self.settings_dict["smtp_port"])

            subject = f"[{course_basics['title']}] Question on the \"{exercise_basics['title']}\" exercise of the \"{assignment_basics['title']}\" assignment"

            success = send_email("Instructor or Teaching Assistant", "no-reply@no-reply.edu", self.user_info["name"], questioner_info["email_address"], smtp_server, smtp_port, subject, message)

            if success:
                return self.write("Success: Your answer has been received, and an email has been sent to the questioner.")
            else:
                return self.write("Error: An error occurred when attempting to send an email notifying the instructor/assistant that the answer was received.")
        except:
            print(traceback.format_exc())
            return self.write("Error: An error occurred either when saving the question or when sending an email notifying the instructor/assistant that the answer was received.")