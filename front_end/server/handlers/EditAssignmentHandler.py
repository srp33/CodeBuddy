from BaseUserHandler import *
import datetime as dt

class EditAssignmentHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id):
        try:
            course_basics = await self.get_course_basics(course_id)
            course_details = await self.get_course_details(course_id)
            assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)

            if self.is_administrator or await self.is_instructor_for_course(course_id):
                percentage_options = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
                hour_options = list(range(13))
                minute_options = list(range(61))

                self.render("edit_assignment.html", courses=self.courses, assignments=self.content.get_assignments(course_basics), course_basics=course_basics, course_details=course_details, assignment_basics=assignment_basics, assignment_details=await self.get_assignment_details(course_basics, assignment_id), percentage_options=percentage_options, hour_options=hour_options, minute_options=minute_options, result=None, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_assistant=await self.is_assistant_for_course(course_id))
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def post(self, course_id, assignment_id):
        try:
            if not self.is_administrator and not await self.is_instructor_for_course(course_id):
                self.render("permissions.html")
                return

            course_basics = await self.get_course_basics(course_id)
            course_details = await self.get_course_details(course_id)
            assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)
            assignment_details = await self.get_assignment_details(course_basics, assignment_id)

            assignment_basics["title"] = self.get_body_argument("title").strip()
            assignment_details["introduction"] = self.get_body_argument("introduction").strip()
            assignment_basics["visible"] = self.get_body_argument("is_visible") == "Yes"
            assignment_details["has_start_date"] = self.get_body_argument("has_start_date") == "Select"
            assignment_details["has_due_date"] = self.get_body_argument("has_due_date") == "Select"
            assignment_details["has_timer"] = self.get_body_argument("has_timer") == "On"
            #assignment_details["enable_help_requests"] = self.get_body_argument("enable_help_requests") == "Yes"
            assignment_details["enable_help_requests"] = False
            assignment_details["allowed_ip_addresses"] = self.get_body_argument("allowed_ip_addresses").strip()
            assignment_details["allowed_external_urls"] = self.get_body_argument("allowed_external_urls")
            assignment_details["use_virtual_assistant"] = self.get_body_argument("use_virtual_assistant")

            if assignment_details["has_start_date"]:
                start_date = self.get_body_argument("start_date_picker").strip()

                if start_date == "None":
                    start_date = None
                else:
                    start_date = dt.datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S.%fZ')
            else:
                start_date = None

            if assignment_details["has_due_date"]:
                due_date = self.get_body_argument("due_date_picker").strip()
                allow_late = self.get_body_argument("allow_late_select") == "Yes"
                late_percent = int(self.get_body_argument("late_percent_select")[:-1]) / 100
                view_answer_late = self.get_body_argument("view_late_select") == "Yes"

                if not allow_late:
                    late_percent = None
                if due_date == "None":
                    due_date = None
                else:
                    due_date = dt.datetime.strptime(due_date, '%Y-%m-%dT%H:%M:%S.%fZ')
            else:
                due_date = None
                allow_late = False
                late_percent = None
                view_answer_late = False

            if assignment_details["has_timer"]:
                hour_timer = int(self.get_body_argument("hour_select"))
                minute_timer = int(self.get_body_argument("minute_select"))
                restrict_other_assignments = self.get_body_argument("restrict_other_assignments_select") == "Yes"
            else:
                hour_timer = None
                minute_timer = None
                restrict_other_assignments = False

            assignment_details["start_date"] = start_date
            assignment_details["due_date"] = due_date
            assignment_details["allow_late"] =  allow_late
            assignment_details["late_percent"] = late_percent
            assignment_details["view_answer_late"] = view_answer_late
            assignment_details["hour_timer"] = hour_timer
            assignment_details["minute_timer"] = minute_timer
            assignment_details["restrict_other_assignments"] = restrict_other_assignments

            result = "Success: Assignment information saved!"

            if assignment_basics["title"] == "" or assignment_details["introduction"] == "":
                result = "Error: Missing title or introduction."
            else:
                if self.content.has_duplicate_title(self.content.get_assignments(course_basics), assignment_basics["id"], assignment_basics["title"]):
                    result = "Error: An assignment with that title already exists."
                else:
                    if len(assignment_basics["title"]) > 100:
                        result = "Error: The title cannot exceed 100 characters."
                    else:
                        if assignment_details["start_date"] and assignment_details["due_date"] and assignment_details["start_date"] > assignment_details["due_date"]:
                            reslt = "Error: The start date must be earlier than the due date."
                        else:
                            if assignment_details["has_timer"] and assignment_details["hour_timer"] == 0 and assignment_details["minute_timer"] == 0:
                                result = "Error: A timer must be longer than zero minutes."
                            else:
                                self.content.specify_assignment_details(assignment_details, assignment_details["introduction"], None, dt.datetime.utcnow(), assignment_details["start_date"], assignment_details["due_date"], assignment_details["allow_late"], assignment_details["late_percent"], assignment_details["view_answer_late"], assignment_details["enable_help_requests"], assignment_details["has_timer"], assignment_details["hour_timer"], assignment_details["minute_timer"], assignment_details["restrict_other_assignments"], assignment_details["allowed_ip_addresses"], assignment_details["allowed_external_urls"], assignment_details["use_virtual_assistant"])

                                assignment_id = self.content.save_assignment(assignment_basics, assignment_details)

                                #    result = "Error: The title can only contain alphanumeric characters, spaces, hyphens, and parentheses."
                                #else:
                                #self.content.specify_assignment_basics(assignment_basics, assignment_basics["title"], assignment_basics["visible"])

            percentage_options = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
            hour_options = list(range(13))
            minute_options = list(range(61))

            self.render("edit_assignment.html", courses=self.courses, assignments=self.content.get_assignments(course_basics), course_basics=course_basics, course_details=course_details, assignment_basics=assignment_basics, assignment_details=assignment_details, percentage_options=percentage_options, hour_options=hour_options, minute_options=minute_options, result=result, user_info=self.user_info, is_administrator=self.is_administrator)
        except Exception as inst:
            render_error(self, traceback.format_exc())