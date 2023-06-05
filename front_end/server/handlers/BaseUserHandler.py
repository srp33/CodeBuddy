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

            self.update_cached_variable("user", "user_info", self.content.get_user_info, self.get_current_user())
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
            # print(f"got here5 - {variable_name}")

        return getattr(self, variable_name)

    def get_content_cookie(self, cookie_key, max_age_days):
        content = self.get_secure_cookie(cookie_key, max_age_days=max_age_days)

        if content:
            return json.loads(content)

    def set_content_cookie(self, cookie_key, serializable_content, expires_days):
        total_headers_size = sum(len(key) + len(value) for key, value in self.request.headers.items())

        if total_headers_size < 838860:
            self.set_secure_cookie(cookie_key, json.dumps(serializable_content, default=str), expires_days = expires_days)

        return serializable_content

    ###############################################
    # Functions that do not use cookie caching
    ###############################################

    async def check_whether_should_show_exercise(self, course, assignment, assignment_details, assignments, courses, assignment_basics, course_basics):
        if self.is_administrator or await self.is_instructor_for_course(course) or await self.is_assistant_for_course(course):
            return True

        curr_datetime = datetime.utcnow()

        if assignment_details["has_timer"]:
            user_start_time = self.content.get_user_assignment_start_time(course, assignment, self.user_info["user_id"])

            if user_start_time == None:
                # This means the student hasn't started the timed assignment.
                self.redirect(f"/assignment/{course}/{assignment}")
            else:
                deadline = user_start_time + timedelta(hours = assignment_details["hour_timer"], minutes = assignment_details["minute_timer"])

                if deadline < curr_datetime:
                    return self.render("unavailable_assignment.html", courses=courses, assignments=assignments, course_basics=course_basics, assignment_basics=assignment_basics, assignment_details=assignment_details, error="timer_has_expired", user_info=self.user_info)

        assignment_status = get_assignment_status(self, course, assignment_details, curr_datetime)

        if assignment_status != "render":
            return self.render("unavailable_assignment.html", courses=courses, assignments=assignments, course_basics=course_basics, assignment_basics=assignment_basics, assignment_details=assignment_details, error=assignment_status, user_info=self.user_info, is_administrator=self.is_administrator)

        if self.content.is_taking_restricted_assignment(self.get_current_user(), assignment):
            return self.render("unavailable_assignment.html", courses=courses, assignments=assignments, course_basics=course_basics, assignment_basics=assignment_basics, assignment_details=assignment_details, error="restrict_other_assignments", user_info=self.user_info, is_administrator=self.is_administrator)

        return True