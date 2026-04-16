# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

import base64
import json
import re

from BaseUserHandler import *


def parse_course_templates_from_request(payload):
    """
    Returns (templates_dict, error_message).
    templates_dict is always a dict suitable for the editor when possible; error_message is None if valid.
    """
    payload = (payload or "").strip()
    if not payload:
        return {}, None
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError:
        return {}, "Error: Templates data was not valid JSON."

    if not isinstance(parsed, dict):
        return {}, "Error: Templates must be a JSON object mapping names to text."

    normalized = {}
    for key, val in parsed.items():
        name = str(key).strip()
        if not name:
            return {}, "Error: Template names cannot be empty."
        if not re.match(r"^[A-Za-z][A-Za-z0-9_]*$", name):
            return {}, "Error: Each template name must start with a letter and contain only letters, digits, and underscores."
        template_text = val if isinstance(val, str) else str(val)
        if "{" in template_text or "}" in template_text:
            return {}, "Error: Template text cannot contain squiggly brackets."
        normalized[name] = template_text

    return normalized, None


def course_templates_to_b64(templates_dict):
    raw = json.dumps(templates_dict or {}, ensure_ascii=False).encode("utf-8")
    return base64.b64encode(raw).decode("ascii")


class EditCourseHandler(BaseUserHandler):
    async def get(self, course_id):
        try:
            course_basics = await self.get_course_basics(course_id)
            course_details = await self.get_course_details(course_id)

            if self.is_administrator or await self.is_instructor_for_course(course_id):
                self.render("edit_course.html", courses=self.courses, assignment_statuses=await self.get_assignment_statuses(course_basics), course_basics=course_basics, course_details=course_details, course_templates_b64=course_templates_to_b64(course_details.get("templates")), result=None, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_edit_page=True)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def post(self, course_id):
        try:
            if not self.is_administrator and not await self.is_instructor_for_course(course_id):
                self.render("permissions.html")
                return

            course_basics = await self.get_course_basics(course_id)
            course_details = await self.get_course_details(course_id)

            course_basics["title"] = self.get_body_argument("title").strip()
            course_basics["visible"] = self.get_body_argument("is_visible") == "Yes"
            course_details["introduction"] = self.get_body_argument("introduction").strip()
            course_details["passcode"] = self.get_body_argument("passcode").strip()

            if course_details["passcode"] == "":
                course_details["passcode"] = None

            course_details["email_address"] = self.get_body_argument("email_address").strip()

            if course_details["email_address"] != "" and not is_valid_email_address(course_details["email_address"]):
                result = "Error: The email address you provided is invalid."
            else:
                new_highlighted = self.get_body_argument("highlighted") == "Yes"
                if not course_details["highlighted"] and new_highlighted and not self.is_administrator:
                    result = "Error: Only an administrator can highlight a course."
                else:
                    course_details["highlighted"] = new_highlighted

                    course_details["allow_students_download_submissions"] = self.get_body_argument("allow_students_download_submissions") == "Yes"

                    virtual_assistant_config = self.get_body_argument("virtual_assistant_config")
                    if virtual_assistant_config.strip() == "":
                        virtual_assistant_config = None
                    course_details["virtual_assistant_config"] = virtual_assistant_config

                    result = "Success: Course information saved!"

                    if course_basics["title"] == "" or course_details["introduction"] == "":
                        result = "Error: Missing title or introduction."
                    else:
                        current_titles = [x[1]["title"] for x in self.courses if x[0] != course_basics["id"]]
                        if course_basics["title"] in current_titles:
                            result = "Error: A course with that title already exists."
                        else:
                            #if re.search(r"[^\w ]", title):
                            #    result = "Error: The title can only contain alphanumeric characters and spaces."
                            #else:
                            if len(course_basics["title"]) > 100:
                                result = "Error: The title cannot exceed 100 characters."
                            else:
                                templates_payload = self.get_body_argument("templates_json", default="{}")
                                normalized_templates, templates_error = parse_course_templates_from_request(templates_payload)

                                if templates_error:
                                    result = templates_error
                                    try:
                                        loose = json.loads(templates_payload.strip() or "{}")
                                        if isinstance(loose, dict):
                                            course_details["templates"] = {str(k).strip(): (v if isinstance(v, str) else str(v)) for k, v in loose.items() if str(k).strip()}
                                    except json.JSONDecodeError:
                                        pass
                                else:
                                    course_details["templates"] = normalized_templates

                                    va_dict = {}
                                    try:
                                        va_dict = load_yaml_dict(virtual_assistant_config)
                                    except:
                                        pass

                                    if virtual_assistant_config is None or (type(va_dict) is dict and "api_key" in va_dict and "model" in va_dict and "temperature" in va_dict and "timeout" in va_dict and "max_per_exercise" in va_dict and type(va_dict["max_per_exercise"]) is int):
                                        self.content.specify_course_details(course_details, course_details["introduction"], course_details["passcode"], course_details["email_address"], course_details["highlighted"], course_details["allow_students_download_submissions"], course_details["virtual_assistant_config"], course_details["templates"], None, get_current_datetime())

                                        course_id = self.content.save_course(course_basics, course_details)
                                    else:
                                        result = "Error: The Virtual Assistant configuration is invalid."

            self.render("edit_course.html", courses=self.courses, assignment_statuses=await self.get_assignment_statuses(course_basics), course_basics=course_basics, course_details=course_details, course_templates_b64=course_templates_to_b64(course_details.get("templates")), result=result, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_assistant=await self.is_assistant_for_course(course_id), is_edit_page=True)
        except Exception as inst:
            render_error(self, traceback.format_exc())