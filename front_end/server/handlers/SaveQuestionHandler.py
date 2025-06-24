# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class SaveQuestionHandler(BaseUserHandler):
    async def post(self, course_id, assignment_id, exercise_id, questioner_id):
        try:
            course_basics = await self.get_course_basics(course_id)
            course_details = await self.get_course_details(course_id)
            assignment_basics = await self.get_assignment_basics(course_basics, assignment_id)
            exercise_basics = await self.get_exercise_basics(course_basics, assignment_basics, exercise_id)

            question = self.get_body_argument("question")
            questioner_share = self.get_body_argument("questioner_share") == "true"

            question_id = self.content.save_question(course_id, assignment_id, exercise_id, questioner_id, question, questioner_share)

            question_url = f"https://{self.settings_dict['domain']}/exercise/{course_id}/{assignment_id}/{exercise_id}"
            answer_url = f"https://{self.settings_dict['domain']}/answer_question/{course_id}/{assignment_id}/{exercise_id}/{question_id}"

            questioner_info = self.content.get_user_info(questioner_id)

            message_to_questioner = f"<p>Thank you for asking the following question.</p><p><pre>{question}</pre></p>"

            if questioner_share:
                message_to_questioner += f"<p>You agreed to have your question (and any answer that is provided) shared with other students in the class (if the instructor decides to share it).</p>"
            else:
                message_to_questioner += f"<p>You indicated that you do NOT want your question shared with other students in the class.</p>"

            message_to_questioner += f"<p>After the question has been answered, a separate email will be sent to you, and an answer may be posted under \"Q & A\" <a href='{question_url}'>here</a>. Please do not reply to this email; instead contact the instructor or a teaching assistant, if needed.</p>"

            message_to_answerer = f"<p>{questioner_info['name']} ({questioner_id}) asked the following question.</p><p><pre>{question}</pre></p><p>Answer it <a href='{answer_url}'>here</a>.</p>"

            smtp_server = self.settings_dict["smtp_server"]
            smtp_port = int(self.settings_dict["smtp_port"])

            subject_to_answerer = f"[{course_basics['title']}] Question from {questioner_info['name']} on the \"{exercise_basics['title']}\" exercise of the \"{assignment_basics['title']}\" assignment"

            subject_to_questioner = f"[{course_basics['title']}] Question on the \"{exercise_basics['title']}\" exercise of the \"{assignment_basics['title']}\" assignment"

            success_to_answerer = send_email(self.user_info["name"], self.user_info["email_address"], "Instructor or Assistant", course_details["email_address"], smtp_server, smtp_port, subject_to_answerer, message_to_answerer)

            success_to_questioner = send_email("Instructor or Teaching Assistant", "no-reply@no-reply.edu", self.user_info["name"], self.user_info["email_address"], smtp_server, smtp_port, subject_to_questioner, message_to_questioner)

            if success_to_answerer and success_to_questioner:
                return self.write(f"Success: Your question has been received. An email was sent to the instructor/assistant(s), and a confirmation was sent to {self.user_info['email_address']}.")
            else:
                return self.write("Error: An error occurred when attempting to send an email notifying the instructor/assistant(s) that the question was submitted.")
        except:
            print(traceback.format_exc())
            return self.write("Error: An error occurred either when saving the question or when sending an email notifying the instructor/assistant that the question was submitted.")