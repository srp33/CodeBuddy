# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class EditCourseHandler(BaseUserHandler):
    async def get(self, course_id):
        try:
            course_basics = await self.get_course_basics(course_id)
            course_details = await self.get_course_details(course_id)

            if self.is_administrator or await self.is_instructor_for_course(course_id):
                self.render("edit_course.html", courses=self.courses, assignment_statuses=await self.get_assignment_statuses(course_basics), course_basics=course_basics, course_details=course_details, result=None, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_edit_page=True)
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

            course_details["allow_students_download_submissions"] = self.get_body_argument("allow_students_download_submissions") == "Yes"

            virtual_assistant_config = self.get_body_argument("virtual_assistant_config")
            if virtual_assistant_config.strip() == "":
                virtual_assistant_config = None
            course_details["virtual_assistant_config"] = virtual_assistant_config

            result = "Success: Course information saved!"

            if course_basics["title"] == "" or course_details["introduction"] == "":
                result = "Error: Missing title or introduction."
            else:
                if self.content.has_duplicate_title(self.courses, course_basics["id"], course_basics["title"]):
                    result = "Error: A course with that title already exists."
                else:
                    #if re.search(r"[^\w ]", title):
                    #    result = "Error: The title can only contain alphanumeric characters and spaces."
                    #else:
                    if len(course_basics["title"]) > 100:
                        result = "Error: The title cannot exceed 100 characters."
                    else:
                        va_dict = {}
                        try:
                            va_dict = load_yaml_dict(virtual_assistant_config)
                        except:
                            pass

                        if virtual_assistant_config is None or (type(va_dict) is dict and "api_key" in va_dict and "model" in va_dict and "temperature" in va_dict and "timeout" in va_dict and "max_per_exercise" in va_dict and type(va_dict["max_per_exercise"]) is int):
                            #self.content.specify_course_basics(course_basics, course_basics["title"], course_basics["visible"])
                            self.content.specify_course_details(course_details, course_details["introduction"], course_details["passcode"], course_details["allow_students_download_submissions"], course_details["virtual_assistant_config"], None, get_current_datetime())

                            course_id = self.content.save_course(course_basics, course_details)
                        else:
                            result = "Error: The Virtual Assistant configuration is invalid."

            self.render("edit_course.html", courses=self.courses, assignment_statuses=await self.get_assignment_statuses(course_basics), course_basics=course_basics, course_details=course_details, result=result, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_assistant=await self.is_assistant_for_course(course_id), is_edit_page=True)
        except Exception as inst:
            render_error(self, traceback.format_exc())