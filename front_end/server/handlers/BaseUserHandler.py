# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseRequestHandler import *
from content import *
import traceback

class BaseUserHandler(BaseRequestHandler):
    ###############################################
    # Overriding functions
    ###############################################
    def prepare(self):
        try:
            super().prepare()

            user_id = self.get_current_user()

            if not user_id:
                redirect_to_login(self, self.request.path)

            self.updated_dict = self.content.find_when_content_updated()

            self.total_headers_size = sum(len(key) + len(value) for key, value in self.request.headers.items())

            self.update_cached_variable("user", "user_info", self.content.get_user_info, self.get_current_user())

            if self.user_info["user_id"] is None:
                self.redirect("/logout")

            self.update_cached_variable("user", "is_administrator", self.content.is_administrator, self.get_current_user())
            self.update_cached_variable("user", "courses", self.content.get_registered_courses, self.get_current_user())
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def on_finish(self):
        try:
            user_id = self.get_current_user()

            additional_message = None
            if user_id:
                additional_message = user_id

            log_page_access(self, additional_message)

            super().on_finish()
        except:
            print(f"Error occurred when attempting to log. {traceback.format_exc()}")
            pass

    ####################################################
    # Functions that cache database contents in cookies
    # for user-related data.
    ####################################################

    async def is_instructor_for_course(self, course_id):
        return self.update_cached_variable(str(course_id), f"is_instructor_{course_id}", self.content.user_has_role, self.get_current_user(), course_id, "instructor")

    async def is_assistant_for_course(self, course_id):
        return self.update_cached_variable(str(course_id), f"is_assistant_{course_id}", self.content.user_has_role, self.get_current_user(), course_id, "assistant")

    ####################################################
    # Functions that cache database contents in cookies
    # for course-related data.
    ####################################################

    async def get_course_basics(self, course_id):
        return self.update_cached_variable(str(course_id), f"course_basics_{course_id}", self.content.get_course_basics, course_id)
    
    async def get_course_details(self, course_id, format_output=False):
        course_details = self.update_cached_variable(str(course_id), f"course_details_{course_id}", self.content.get_course_details, course_id)

        if format_output:
            course_details["introduction"] = convert_markdown_to_html(course_details["introduction"])

        return course_details

    async def get_assignments(self, course_basics):
        course_id = course_basics["id"]

        assignments_raw = self.update_cached_variable(str(course_id), f"assignments_{course_id}", self.content.get_assignments, course_basics)

        assignments = []
        for assignment in assignments_raw:
            del assignment[1]["visible"]
            assignments.append(assignment)

        return assignments
    
    async def get_assignment_basics(self, course_basics, assignment_id):
        course_id = course_basics["id"]

        assignment_basics = self.update_cached_variable(str(course_id), f"assignment_basics_{course_id}_{assignment_id}", self.content.get_assignment_basics, course_basics, assignment_id)

        del assignment_basics["visible"]
        del assignment_basics["course"]

        return assignment_basics
    
    async def get_assignment_details(self, course_basics, assignment_id, format_output=False):
        # course_id = course_basics["id"]

        # assignment_details = self.update_cached_variable(str(course_id), f"assignment_details_{course_id}_{assignment_id}", self.content.get_assignment_details, course_basics, assignment_id)

        assignment_details = self.content.get_assignment_details(course_basics, assignment_id)

        if format_output:
            assignment_details["introduction"] = convert_markdown_to_html(assignment_details["introduction"])

        return assignment_details
    
    async def get_exercise_basics(self, course_basics, assignment_basics, exercise_id):
        course_id = course_basics["id"]
        assignment_id = assignment_basics["id"]

        exercise_basics = self.update_cached_variable(str(course_id), f"exercise_basics_{course_id}_{assignment_id}_{exercise_id}", self.content.get_exercise_basics, course_basics, assignment_basics, exercise_id)

        del exercise_basics["visible"]
        del exercise_basics["assignment"]

        return exercise_basics
    
    async def get_exercise_details(self, course_basics, assignment_basics, exercise_id):
        # course_id = course_basics["id"]
        # assignment_id = assignment_basics["id"]

        # return self.update_cached_variable(str(course_id), f"exercise_details_{course_id}_{assignment_id}_{exercise_id}", self.content.get_exercise_details, course_basics, assignment_basics, exercise_id)

        return self.content.get_exercise_details(course_basics, assignment_basics, exercise_id)

    async def get_partner_info(self, course_id, exclude_self):
        partner_info = self.update_cached_variable(str(course_id), f"partner_info_{course_id}", self.content.get_partner_info, course_id)

        if exclude_self and self.user_info["name"] in partner_info:
            del partner_info[self.user_info["name"]]

        return partner_info
    
    ###################################################
    # Functions that help with managing cookies
    ###################################################

    def update_cached_variable(self, update_key, variable_name, function_name, *args, **kwargs):
        if not hasattr(self, variable_name):
            cookie_expiration_days = 30 if update_key == "user" else 1

            update_cookie = self.get_content_cookie(update_key, cookie_expiration_days)

            if update_cookie:
                if update_key in self.updated_dict and update_cookie == self.updated_dict[update_key]:
                    variable_cookie = self.get_content_cookie(variable_name, cookie_expiration_days)

                    if variable_cookie == None:
                        setattr(self, variable_name, self.set_content_cookie(variable_name, function_name(*args, **kwargs), cookie_expiration_days))
                        # print(f"got here1 - {variable_name}")
                    else:
                        setattr(self, variable_name, variable_cookie)
                        # print(f"got here2 - {variable_name} - {variable_cookie}")
                else:
                    setattr(self, variable_name, self.set_content_cookie(variable_name, function_name(*args, **kwargs), cookie_expiration_days))
                    # print(f"got here3 - {variable_name}")

                    if update_key in self.updated_dict:
                        # print(f"got here3.1 - {variable_name}")
                        self.set_content_cookie(update_key, self.updated_dict[update_key], cookie_expiration_days)
            else:
                if update_key in self.updated_dict:
                    self.set_content_cookie(update_key, self.updated_dict[update_key], cookie_expiration_days)

                setattr(self, variable_name, self.set_content_cookie(variable_name, function_name(*args, **kwargs), cookie_expiration_days))
                # print(f"got here4 - {variable_name}")
        # else:
        #     print(f"got here5 - {variable_name}")

        return getattr(self, variable_name)

    def get_content_cookie(self, cookie_key, max_age_days):
        content = self.get_secure_cookie(cookie_key, max_age_days=max_age_days)

        if content:
            return ujson.loads(content)

    def set_content_cookie(self, cookie_key, serializable_content, expires_days):
        if self.total_headers_size > 4096:
            self.clear_cookie(cookie_key)
            return serializable_content

        content = ujson.dumps(serializable_content, default=str)

        # We have to guess how much header space the cookie will take.
        # This is a conservative guess.
        estimated_cookie_size = len(content) * 1.33 + 150 

        if self.total_headers_size + estimated_cookie_size > 4096:
            self.clear_cookie(cookie_key)
            return serializable_content

        self.set_secure_cookie(cookie_key, content, expires_days = expires_days)
        self.total_headers_size += estimated_cookie_size

        return serializable_content

    ###############################################
    # Functions that do not use cookie caching
    ###############################################

    async def check_whether_should_show_exercise(self, course_id, assignment_id, assignment_details, assignments, courses, assignment_basics, course_basics):
        if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
            return True

        if assignment_details["has_timer"]:
            timer_status, __, __, __, __ = get_student_timer_status(self.content, course_id, assignment_id, assignment_details, self.user_info["user_id"])

            if timer_status != "timer_in_progress":
                self.redirect(f"/assignment/{course_id}/{assignment_id}")
                return

        assignment_status = get_assignment_status(self, course_id, assignment_details, datetime.utcnow())

        if assignment_status != "render":
            return self.render("unavailable_assignment.html", courses=courses, assignments=assignments, course_basics=course_basics, assignment_basics=assignment_basics, assignment_details=assignment_details, error=assignment_status, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id))

        if self.content.is_taking_restricted_assignment(self.get_current_user(), assignment_id):
            return self.render("unavailable_assignment.html", courses=courses, assignments=assignments, course_basics=course_basics, assignment_basics=assignment_basics, assignment_details=assignment_details, error="restrict_other_assignments", user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id))

        if len(await self.get_prerequisite_assignments_uncompleted(course_id, assignment_details)) > 0:
            return self.render("unavailable_assignment.html", courses=courses, assignments=assignments, course_basics=course_basics, assignment_basics=assignment_basics, assignment_details=assignment_details, error="prerequisite_assignments_uncompleted", user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id))

        return True
    
    async def get_prerequisite_assignments_uncompleted(self, course_id, assignment_details):
        prerequisite_assignments_not_completed = []

        for assignment_status in await self.content.get_assignment_statuses(course_id, self.get_current_user(), show_hidden=False):
            if assignment_status[0] in assignment_details["prerequisite_assignment_ids"] and not assignment_status[1]["passed"]:
                prerequisite_assignments_not_completed.append([assignment_status[0], assignment_status[1]["title"]])

        return prerequisite_assignments_not_completed