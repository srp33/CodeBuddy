# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class EmailStudentsHandler(BaseUserHandler):
    async def post(self, course_id, assignment_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                student_ids = self.get_arguments("selected_student")
                students = []
                for sid in student_ids:
                    info = self.content.get_user_info(sid)
                    students.append({"name": info["name"] or sid, "student_id": sid, "email_address": info.get("email_address") or ""})

                course_basics = await self.get_course_basics(course_id)
                assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)
                course_details = await self.get_course_details(course_id)
                email_configured = is_email_configured(self.settings_dict, course_details)

                email_message = self.get_body_argument("email_message", default=None)
                email_result = None

                if email_configured and email_message is not None and email_message.strip() != "" and len(students) > 0:
                    try:
                        smtp_server = self.settings_dict.get("smtp_server", "").strip()
                        smtp_port_str = str(self.settings_dict.get("smtp_port", "")).strip()
                        if smtp_server and smtp_port_str:
                            from_address = (course_details.get("email_address") or "").strip() or self.user_info.get("email_address") or ""
                            from_name = course_basics.get("title") or self.user_info.get("name") or "Instructor"
                            if not from_address or not is_valid_email_address(from_address):
                                from_address = self.user_info.get("email_address") or ""
                                from_name = self.user_info.get("name") or "Instructor"

                            subject = f"[{course_basics['title']}] Message from your instructor: {assignment_basics['title']}"
                            body_html = f"<p>{email_message.strip().replace(chr(10), '<br>')}</p>"

                            num_sent = 0
                            failed = []
                            # For testing: send all emails to stephen_piccolo@byu.edu instead of each student's address.
                            test_email = "stephen_piccolo@byu.edu"
                            for s in students:
                                # to_address = (s.get("email_address") or "").strip()
                                # if not to_address or not is_valid_email_address(to_address):
                                #     failed.append(f"{s['name']} ({s['student_id']}) — no valid email")
                                #     continue
                                to_address = test_email
                                success = send_email(from_name, from_address, s["name"], to_address, smtp_server, int(smtp_port_str), subject, body_html)
                                if success:
                                    num_sent += 1
                                else:
                                    failed.append(f"{s['name']} ({s['student_id']})")

                            email_result = {"num_sent": num_sent, "failed": failed, "success": num_sent > 0}
                    except Exception:
                        email_result = {"error": "Could not send email. If this continues, please contact the administrator."}

                self.render("email_students.html", courses=self.courses, course_basics=course_basics, assignment_basics=assignment_basics, assignment_statuses=await self.get_assignment_statuses(course_basics), students=students, email_result=email_result, email_configured=email_configured, user_info=self.user_info, is_administrator=self.is_administrator)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())
