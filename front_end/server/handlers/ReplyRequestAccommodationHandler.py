# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

import html
import traceback

from BaseUserHandler import *


class ReplyRequestAccommodationHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id, student_id):
        try:
            if not (self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id)):
                self.render("permissions.html")
                return

            course_basics = await self.get_course_basics(course_id)
            if not course_basics["exists"]:
                self.render("reply_request_accommodation.html",
                    courses=self.courses,
                    course_basics=course_basics,
                    assignment_basics={"id": "", "title": "", "exists": False},
                    student_info=None,
                    already_granted=False,
                    email_sent=False,
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
                    error="This assignment does not exist.",
                    assignment_statuses=await self.get_assignment_statuses(course_basics),
                    user_info=self.user_info,
                    is_administrator=self.is_administrator,
                    is_instructor=await self.is_instructor_for_course(course_id),
                    is_assistant=await self.is_assistant_for_course(course_id),
                )
                return

            student_info = self.content.get_user_info(student_id)
            already_granted = self.content.student_has_late_exception(course_id, assignment_id, student_id)
            email_sent = False

            if not already_granted:
                self.content.add_student_late_exception(course_id, assignment_id, student_id)

                course_details = await self.get_course_details(course_id)
                student_email = (student_info.get("email_address") or "").strip()

                if is_email_configured(self.settings_dict, course_details):
                    from_address = (course_details.get("email_address") or "").strip()
                    from_name = course_basics.get("title") or "Your instructor"
                    student_name = student_info.get("name") or student_id
                    # TODO: replace with student_email once testing is complete
                    student_email = from_address

                    course_title_escaped = html.escape(course_basics["title"])
                    assignment_title_escaped = html.escape(assignment_basics["title"])
                    student_name_escaped = html.escape(student_name)
                    student_id_escaped = html.escape(student_id)
                    assignment_url = f"https://{(self.settings_dict.get('domain') or '').strip()}/assignment/{course_id}/{assignment_id}"
                    assignment_url_escaped = html.escape(assignment_url)

                    body = f"""
<p>Your accommodation request has been <strong>approved</strong>.</p>
<table style="border-collapse:collapse;margin-bottom:1em;">
  <tr><td style="padding:4px 12px 4px 0;font-weight:bold;">Course:</td><td style="padding:4px 0;">{course_title_escaped}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;font-weight:bold;">Assignment:</td><td style="padding:4px 0;">{assignment_title_escaped}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;font-weight:bold;">Student:</td><td style="padding:4px 0;">{student_name_escaped} ({student_id_escaped})</td></tr>
</table>
<p>You may now submit <a href="{assignment_url_escaped}">{assignment_title_escaped}</a> late.</p>
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
                error=None,
                assignment_statuses=await self.get_assignment_statuses(course_basics),
                user_info=self.user_info,
                is_administrator=self.is_administrator,
                is_instructor=await self.is_instructor_for_course(course_id),
                is_assistant=await self.is_assistant_for_course(course_id),
            )
        except Exception:
            render_error(self, traceback.format_exc())
