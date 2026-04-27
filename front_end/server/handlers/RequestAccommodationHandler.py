# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

import html
import traceback

from BaseUserHandler import *

REQUEST_TYPES = {
    "late_submission": "Submit this assignment late",
    "extended_time": "Time and a half on the time limit",
}


class RequestAccommodationHandler(BaseUserHandler):
    async def user_may_access_course(self, course_id):
        if self.is_administrator:
            return True
        if await self.is_instructor_for_course(course_id):
            return True
        if await self.is_assistant_for_course(course_id):
            return True
        registered = self.content.get_registered_students(course_id)
        return self.user_info["user_id"] in [r[0] for r in registered]

    async def render_form(
        self,
        course_basics,
        assignment_basics,
        *,
        form_error=None,
        submit_success=False,
        last_comment="",
        last_request_type="late_submission",
    ):
        course_id = course_basics["id"]
        if course_basics["exists"] and assignment_basics["exists"]:
            assignment_statuses = await self.get_assignment_statuses(course_basics)
            assignment_details = self.content.get_assignment_details(course_basics, assignment_basics["id"])
            course_details = await self.get_course_details(course_id)
            email_configured = is_email_configured(self.settings_dict, course_details)
            is_instr = await self.is_instructor_for_course(course_id)
            is_asst = await self.is_assistant_for_course(course_id)
        elif course_basics["exists"]:
            assignment_statuses = await self.get_assignment_statuses(course_basics)
            assignment_details = {"has_timer": False}
            course_details = await self.get_course_details(course_id)
            email_configured = is_email_configured(self.settings_dict, course_details)
            is_instr = await self.is_instructor_for_course(course_id)
            is_asst = await self.is_assistant_for_course(course_id)
        else:
            assignment_statuses = []
            assignment_details = {"has_timer": False}
            email_configured = False
            is_instr = False
            is_asst = False

        self.render(
            "request_accommodation.html",
            courses=self.courses,
            course_basics=course_basics,
            assignment_basics=assignment_basics,
            assignment_details=assignment_details,
            assignment_statuses=assignment_statuses,
            request_types=REQUEST_TYPES,
            email_configured=email_configured,
            form_error=form_error,
            submit_success=submit_success,
            last_comment=last_comment,
            last_request_type=last_request_type,
            accommodation_request_message=(self.settings_dict.get("accommodation_request_message") or "").strip(),
            user_info=self.user_info,
            is_administrator=self.is_administrator,
            is_instructor=is_instr,
            is_assistant=is_asst,
        )

    async def get(self, course_id, assignment_id):
        try:
            course_basics = await self.get_course_basics(course_id)
            if not course_basics["exists"]:
                null_assignment = {"id": "", "title": "", "visible": True, "exists": False, "course": course_basics}
                await self.render_form(course_basics, null_assignment)
                return
            assignment_basics = await self.get_assignment_basics(course_basics, assignment_id)
            if not assignment_basics["exists"]:
                await self.render_form(course_basics, assignment_basics)
                return
            if not await self.user_may_access_course(course_id):
                self.render("permissions.html")
                return
            await self.render_form(course_basics, assignment_basics)
        except Exception:
            render_error(self, traceback.format_exc())

    async def post(self, course_id, assignment_id):
        try:
            course_basics = await self.get_course_basics(course_id)
            if not course_basics["exists"]:
                null_assignment = {"id": "", "title": "", "visible": True, "exists": False, "course": course_basics}
                await self.render_form(course_basics, null_assignment)
                return
            assignment_basics = await self.get_assignment_basics(course_basics, assignment_id)
            if not assignment_basics["exists"]:
                await self.render_form(course_basics, assignment_basics, form_error="This assignment does not exist.")
                return
            if not await self.user_may_access_course(course_id):
                self.render("permissions.html")
                return

            request_type = self.get_body_argument("request_type", default="")
            comments = self.get_body_argument("comments", default="")

            if request_type not in REQUEST_TYPES:
                await self.render_form(
                    course_basics,
                    assignment_basics,
                    form_error="Please select a valid accommodation type.",
                    last_comment=comments,
                )
                return

            if not comments or not str(comments).strip():
                await self.render_form(
                    course_basics,
                    assignment_basics,
                    form_error="Please enter comments explaining your request.",
                    last_comment=comments or "",
                    last_request_type=request_type,
                )
                return

            course_details = await self.get_course_details(course_id)
            if not is_email_configured(self.settings_dict, course_details):
                await self.render_form(
                    course_basics,
                    assignment_basics,
                    form_error="This page cannot send email right now. Please contact your instructor or teaching assistant.",
                    last_comment=comments,
                    last_request_type=request_type,
                )
                return

            from_address = (self.user_info.get("email_address") or "").strip()
            if not from_address or not is_valid_email_address(from_address):
                await self.render_form(
                    course_basics,
                    assignment_basics,
                    form_error="Your account does not have a valid email address. Update your profile, then try again.",
                    last_comment=comments,
                    last_request_type=request_type,
                )
                return

            to_address = (course_details.get("email_address") or "").strip()
            comments_stripped = comments.strip()
            student_name = self.user_info.get("name") or ""
            student_id = self.user_info.get("user_id") or ""
            request_label = REQUEST_TYPES[request_type]

            domain = (self.settings_dict.get("domain") or "").strip()
            approval_url = f"https://{domain}/reply_request_accommodation/{course_id}/{assignment_id}/{student_id}/{request_type}"

            course_title_escaped = html.escape(course_basics['title'])
            assignment_title_escaped = html.escape(assignment_basics['title'])
            student_name_escaped = html.escape(student_name)
            student_id_escaped = html.escape(student_id)
            comments_escaped = html.escape(comments_stripped)
            request_label_escaped = html.escape(request_label)
            approval_url_escaped = html.escape(approval_url)

            body = f"""
<p>An accommodation request has been submitted through CodeBuddy.</p>
<table style="border-collapse:collapse;margin-bottom:1em;">
  <tr><td style="padding:4px 12px 4px 0;font-weight:bold;">Course:</td><td style="padding:4px 0;">{course_title_escaped}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;font-weight:bold;">Assignment:</td><td style="padding:4px 0;">{assignment_title_escaped}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;font-weight:bold;">Student:</td><td style="padding:4px 0;">{student_name_escaped} ({student_id_escaped})</td></tr>
  <tr><td style="padding:4px 12px 4px 0;font-weight:bold;">Request type:</td><td style="padding:4px 0;">{request_label_escaped}</td></tr>
</table>
<p><strong>Justification:</strong></p>
<p style="white-space:pre-wrap;background:#f5f5f5;padding:12px;border-radius:4px;">{comments_escaped}</p>
<hr>
<p>
  <strong>To approve this request</strong>, click the link below:<br>
  <a href="{approval_url_escaped}">{approval_url_escaped}</a>
</p>
<p>
  <strong>To deny this request</strong>, simply reply to this email to explain your decision to the student.
</p>
"""

            subject = f"[{course_basics['title']}] Accommodation Request for {assignment_basics['title']}"

            smtp_server = (self.settings_dict.get("smtp_server") or "").strip()
            smtp_port = int(str(self.settings_dict.get("smtp_port") or "0"))

            ok = send_email(
                student_name,
                from_address,
                "Course instructor",
                to_address,
                smtp_server,
                smtp_port,
                subject,
                body,
            )

            if not ok:
                await self.render_form(
                    course_basics,
                    assignment_basics,
                    form_error="The message could not be sent. Please try again later or contact your instructor directly.",
                    last_comment=comments,
                    last_request_type=request_type,
                )
                return

            await self.render_form(course_basics, assignment_basics, submit_success=True)
        except Exception:
            render_error(self, traceback.format_exc())
