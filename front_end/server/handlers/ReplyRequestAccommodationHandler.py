# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

import html
import math
import traceback

from BaseUserHandler import *


class ReplyRequestAccommodationHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id, student_id, request_type):
        try:
            if not (self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id)):
                self.render("permissions.html")
                return

            if request_type not in ACCOMMODATION_REQUEST_TYPES:
                self.render("reply_request_accommodation.html",
                    courses=self.courses,
                    course_basics={"id": course_id, "title": "", "exists": True},
                    assignment_basics={"id": assignment_id, "title": "", "exists": True},
                    student_info=None,
                    already_granted=False,
                    email_sent=False,
                    request_type=request_type,
                    accommodation_label="",
                    error="Invalid accommodation type.",
                    assignment_statuses=[],
                    user_info=self.user_info,
                    is_administrator=self.is_administrator,
                    is_instructor=await self.is_instructor_for_course(course_id),
                    is_assistant=await self.is_assistant_for_course(course_id),
                )
                return

            accommodation_label = ACCOMMODATION_REQUEST_TYPES[request_type]

            course_basics = await self.get_course_basics(course_id)
            if not course_basics["exists"]:
                self.render("reply_request_accommodation.html",
                    courses=self.courses,
                    course_basics=course_basics,
                    assignment_basics={"id": "", "title": "", "exists": False},
                    student_info=None,
                    already_granted=False,
                    email_sent=False,
                    request_type=request_type,
                    accommodation_label=accommodation_label,
                    error="This course does not exist.",
                    assignment_statuses=[],
                    user_info=self.user_info,
                    is_administrator=self.is_administrator,
                    is_instructor=await self.is_instructor_for_course(course_id),
                    is_assistant=await self.is_assistant_for_course(course_id),
                )
                return

            assignment_basics = await self.get_assignment_basics(course_basics, assignment_id)
            if not assignment_basics["exists"]:
                self.render("reply_request_accommodation.html",
                    courses=self.courses,
                    course_basics=course_basics,
                    assignment_basics=assignment_basics,
                    student_info=None,
                    already_granted=False,
                    email_sent=False,
                    request_type=request_type,
                    accommodation_label=accommodation_label,
                    error="This assignment does not exist.",
                    assignment_statuses=await self.get_assignment_statuses(course_basics),
                    user_info=self.user_info,
                    is_administrator=self.is_administrator,
                    is_instructor=await self.is_instructor_for_course(course_id),
                    is_assistant=await self.is_assistant_for_course(course_id),
                )
                return

            student_info = self.content.get_user_info(student_id)

            if request_type == "late_submission":
                already_granted = self.content.student_has_late_exception(course_id, assignment_id, student_id)
            else:
                already_granted = self.content.student_has_timer_exception(course_id, assignment_id, student_id)

            email_sent = False

            if not already_granted:
                assignment_details = self.content.get_assignment_details(course_basics, assignment_id)

                if request_type == "late_submission":
                    self.content.add_student_late_exception(course_id, assignment_id, student_id)
                else:
                    total_minutes = assignment_details["hour_timer"] * 60 + assignment_details["minute_timer"]
                    extended_minutes = math.ceil(total_minutes * 1.5)
                    new_hours = extended_minutes // 60
                    new_minutes = extended_minutes % 60
                    self.content.add_student_timer_exception(course_id, assignment_id, student_id, new_hours, new_minutes)

                course_details = await self.get_course_details(course_id)
                student_name = student_info.get("name") or student_id
                student_email = (student_info.get("email_address") or "").strip()

                if is_email_configured(self.settings_dict, course_details):
                    from_address = (course_details.get("email_address") or "").strip()
                    from_name = course_basics.get("title") or "Your instructor"

                    course_title_escaped = html.escape(course_basics["title"])
                    assignment_title_escaped = html.escape(assignment_basics["title"])
                    student_name_escaped = html.escape(student_name)
                    student_id_escaped = html.escape(student_id)
                    accommodation_label_escaped = html.escape(accommodation_label)
                    assignment_url = f"https://{(self.settings_dict.get('domain') or '').strip()}/assignment/{course_id}/{assignment_id}"
                    assignment_url_escaped = html.escape(assignment_url)

                    if request_type == "late_submission":
                        action_line = f'<p>You may now submit <a href="{assignment_url_escaped}">{assignment_title_escaped}</a> after the original deadline.</p>'
                    else:
                        action_line = f'<p>Your time limit for <a href="{assignment_url_escaped}">{assignment_title_escaped}</a> has been extended to time and a half.</p>'

                    security_code_row = ""
                    if request_type == "late_submission" and assignment_details.get("require_security_codes", 0) != 0:
                        student_security_code = self.content.get_student_security_code(course_id, assignment_id, student_id)
                        if student_security_code:
                            security_code_escaped = html.escape(student_security_code)
                            security_code_row = f'  <tr><td style="padding:4px 12px 4px 0;font-weight:bold;">Security code:</td><td style="padding:4px 0;font-family:monospace;">{security_code_escaped}</td></tr>\n'

                    body = f"""
<p>Your accommodation request has been <strong>approved</strong>.</p>
<table style="border-collapse:collapse;margin-bottom:1em;">
  <tr><td style="padding:4px 12px 4px 0;font-weight:bold;">Course:</td><td style="padding:4px 0;">{course_title_escaped}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;font-weight:bold;">Assignment:</td><td style="padding:4px 0;">{assignment_title_escaped}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;font-weight:bold;">Student:</td><td style="padding:4px 0;">{student_name_escaped} ({student_id_escaped})</td></tr>
  <tr><td style="padding:4px 12px 4px 0;font-weight:bold;">Accommodation type:</td><td style="padding:4px 0;">{accommodation_label_escaped}</td></tr>
{security_code_row}</table>
{action_line}
<p>Contact the instructor if you have questions.</p>
"""
                    subject = f"[{course_basics['title']}] Accommodation Request Approved: {assignment_basics['title']}"
                    smtp_server = (self.settings_dict.get("smtp_server") or "").strip()
                    smtp_port = int(str(self.settings_dict.get("smtp_port") or "0"))
                    email_sent = send_email(from_name, from_address, student_name, student_email, smtp_server, smtp_port, subject, body)

            self.render("reply_request_accommodation.html",
                courses=self.courses,
                course_basics=course_basics,
                assignment_basics=assignment_basics,
                student_info=student_info,
                already_granted=already_granted,
                email_sent=email_sent,
                request_type=request_type,
                accommodation_label=accommodation_label,
                error=None,
                assignment_statuses=await self.get_assignment_statuses(course_basics),
                user_info=self.user_info,
                is_administrator=self.is_administrator,
                is_instructor=await self.is_instructor_for_course(course_id),
                is_assistant=await self.is_assistant_for_course(course_id),
            )
        except Exception:
            render_error(self, traceback.format_exc())
