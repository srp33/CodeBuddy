# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class AssignmentHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id):
        try:
            course_basics = await self.get_course_basics(course_id)
            assignment_basics = await self.get_assignment_basics(course_basics, assignment_id)
            assignment_details = await self.get_assignment_details(course_basics, assignment_id, True)

            self.add_external_url_dict(assignment_details)
            set_assignment_due_date_passed(assignment_details)

            timer_status = None
            timer_start_time = None
            timer_hours = None
            timer_minutes = None
            timer_deadline = None

            if assignment_details["has_timer"]:
                timer_status, timer_start_time, timer_hours, timer_minutes, timer_deadline = get_student_timer_status(self.content, course_id, assignment_id, assignment_details, self.user_info["user_id"])

            await self.render_page(course_basics, assignment_basics, assignment_details, timer_status, timer_start_time, timer_hours, timer_minutes, timer_deadline)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def post(self, course_id, assignment_id):
        try:
            task = self.request.body.decode()

            course_basics = await self.get_course_basics(course_id)
            assignment_details = await self.get_assignment_details(course_basics, assignment_id, True)

            if task == "start_timer":
                timer_start_time = get_current_datetime()
                
                __, __, __, __, timer_deadline = self.content.set_user_assignment_start_time(course_id, assignment_id, assignment_details, self.user_info["user_id"], timer_start_time)

                self.write(f"Success: {timer_deadline}")
            elif task == "stop_timer":
                self.content.end_timed_assignment_early(course_id, assignment_id, self.user_info["user_id"])
                self.write("Success")
        except Exception as inst:
            self.write(f"Error: {traceback.format_exc()}")

    async def render_page(self, course_basics, assignment_basics, assignment_details, timer_status, timer_start_time, timer_hours, timer_minutes, timer_deadline):
        course_id = course_basics["id"]
        assignment_id = assignment_basics["id"]

        if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
            exercise_statuses = self.content.get_exercise_statuses(course_id, assignment_id, None, show_hidden=True)
            has_non_default_weight = len([x[1]["weight"] for x in exercise_statuses if x[1]["weight"] != 1.0]) > 0
            exercise_summary_scores = self.content.get_exercise_summary_scores(course_basics, assignment_basics)

            return self.render("assignment_admin.html", courses=self.courses, assignment_statuses=await self.get_assignment_statuses(course_basics), exercises=self.content.get_exercises(course_basics, assignment_basics, show_hidden=True), exercise_statuses=exercise_statuses, has_non_default_weight=has_non_default_weight, course_basics=course_basics, assignment_basics=assignment_basics, assignment_details=assignment_details, course_options=[x[1] for x in self.courses if str(x[0]) != course_id], exercise_summary_scores=exercise_summary_scores, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_assistant=await self.is_assistant_for_course(course_id), download_file_name=get_scores_download_file_name(assignment_basics))

        assignment_statuses = await self.get_assignment_statuses(course_basics)
        assignment_is_complete = len([x for x in assignment_statuses if x[0] == assignment_basics["id"] and x[2]["completed"]]) > 0

        render_status = get_assignment_status(self, course_id, assignment_id, assignment_details, get_current_datetime(), self.get_current_user())

        if render_status == "render":
            prerequisite_assignments_not_completed = await self.get_prerequisite_assignments_not_completed(course_id, assignment_details, self.get_current_user())

            if len(prerequisite_assignments_not_completed) > 0:
                return self.render("unavailable_assignment.html", courses=self.courses, assignment_statuses=assignment_statuses, course_basics=course_basics, assignment_basics=assignment_basics, assignment_details=assignment_details, error="prerequisite_assignments_not_completed", prerequisite_assignments_not_completed=prerequisite_assignments_not_completed, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id))

            confirmation_code = None

            if assignment_details["require_security_codes"]:
                confirmation_code = self.content.has_verified_security_code(course_id, assignment_id, self.get_current_user())

                if not confirmation_code:
                    return self.render("verify_security_code.html", courses=self.courses, course_basics=course_basics, assignment_basics=assignment_basics, assignment_details=assignment_details, assignment_statuses=assignment_statuses, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_assistant=await self.is_assistant_for_course(course_id))

            exercise_statuses = self.content.get_exercise_statuses(course_id, assignment_id, self.get_current_user())
            
            has_non_default_weight = len([x[1]["weight"] for x in exercise_statuses if x[1]["weight"] != 1.0]) > 0

            custom_scoring_list = []
            if assignment_details["custom_scoring"] != "":
                custom_scoring_list = json.loads(assignment_details["custom_scoring"])

            return self.render("assignment.html", courses=self.courses, assignment_statuses=assignment_statuses, assignment_is_complete=assignment_is_complete, exercise_statuses=exercise_statuses, has_non_default_weight=has_non_default_weight, course_basics=course_basics, assignment_basics=assignment_basics,assignment_details=assignment_details, custom_scoring_list=custom_scoring_list, 
            timer_status=timer_status, timer_start_time=timer_start_time, timer_hours=timer_hours, timer_minutes=timer_minutes, timer_deadline=timer_deadline, confirmation_code=confirmation_code, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_assistant=await self.is_assistant_for_course(course_id))
        else:
            return self.render("unavailable_assignment.html", courses=self.courses, assignment_statuses=assignment_statuses, course_basics=course_basics, assignment_basics=assignment_basics, assignment_details=assignment_details, error=render_status, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id))
        
    def add_external_url_dict(self, assignment_details):
        if assignment_details["allowed_external_urls"] != "":
            assignment_details["allowed_external_urls_dict"] = {}
            
            if assignment_details["allowed_external_urls"]:
                for url in assignment_details["allowed_external_urls"].split("\n"):
                    url = url.strip()
                    assignment_details["allowed_external_urls_dict"][url] = urllib.parse.quote(url)