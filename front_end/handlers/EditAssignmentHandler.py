import sys
sys.path.append("..")
from StaticFileHandler import *
from helper import *
import traceback
from BaseUserHandler import *
import datetime as dt
from content import *

settings_dict = load_yaml_dict(read_file("/Settings.yaml"))
content = Content(settings_dict)

class EditAssignmentHandler(BaseUserHandler):
    def get(self, course, assignment):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                percentage_options = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
                hour_options = list(range(13))
                minute_options = list(range(61))

                self.render("edit_assignment.html", courses=content.get_courses(), assignments=content.get_assignments(course), exercises=content.get_exercises(course, assignment), exercise_statuses=content.get_exercise_statuses(course, assignment, self.get_user_info()["user_id"]), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), assignment_details=content.get_assignment_details(course, assignment), percentage_options=percentage_options, hour_options=hour_options, minute_options=minute_options, result=None, user_info=self.get_user_info())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course, assignment):
        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course) and not self.is_assistant_for_course(course):
                self.render("permissions.html")
                return

            assignment_basics = content.get_assignment_basics(course, assignment)
            assignment_details = content.get_assignment_details(course, assignment)

            assignment_basics["title"] = self.get_body_argument("title").strip()
            assignment_details["introduction"] = self.get_body_argument("introduction").strip()
            assignment_basics["visible"] = self.get_body_argument("is_visible") == "Yes"
            assignment_details["has_start_date"] = self.get_body_argument("has_start_date") == "Select"
            assignment_details["has_due_date"] = self.get_body_argument("has_due_date") == "Select"
            assignment_details["has_timer"] = self.get_body_argument("has_timer") == "On"
            assignment_details["enable_help_requests"] = self.get_body_argument("enable_help_requests") == "Yes"
            assignment_details["allowed_ip_addresses"] = [x.strip() for x in self.get_body_argument("allowed_ip_addresses").split(",") if x != "" and x != ","]

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
            else:
                hour_timer = None
                minute_timer = None

            assignment_details["start_date"] = start_date
            assignment_details["due_date"] = due_date
            assignment_details["allow_late"] =  allow_late
            assignment_details["late_percent"] = late_percent
            assignment_details["view_answer_late"] = view_answer_late
            assignment_details["hour_timer"] = hour_timer
            assignment_details["minute_timer"] = minute_timer

            result = "Success: Assignment information saved!"

            if assignment_basics["title"] == "" or assignment_details["introduction"] == "":
                result = "Error: Missing title or introduction."
            else:
                if content.has_duplicate_title(content.get_assignments(course), assignment_basics["id"], assignment_basics["title"]):
                    result = "Error: An assignment with that title already exists."
                else:
                    if len(assignment_basics["title"]) > 80:
                        result = "Error: The title cannot exceed 80 characters."
                    else:
                        if assignment_details["start_date"] and assignment_details["due_date"] and assignment_details["start_date"] > assignment_details["due_date"]:
                            result = "Error: The start date must be earlier than the due date."
                        else:
                            #    result = "Error: The title can only contain alphanumeric characters, spaces, hyphens, and parentheses."
                            #else:
                            #content.specify_assignment_basics(assignment_basics, assignment_basics["title"], assignment_basics["visible"])
                            content.specify_assignment_details(assignment_details, assignment_details["introduction"], None, dt.datetime.now(), assignment_details["start_date"], assignment_details["due_date"], assignment_details["allow_late"], assignment_details["late_percent"], assignment_details["view_answer_late"], assignment_details["enable_help_requests"], assignment_details["has_timer"], assignment_details["hour_timer"], assignment_details["minute_timer"], assignment_details["allowed_ip_addresses"])
                            assignment = content.save_assignment(assignment_basics, assignment_details)

            percentage_options = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
            hour_options = list(range(13))
            minute_options = list(range(61))

            self.render("edit_assignment.html", courses=content.get_courses(), assignments=content.get_assignments(course), exercises=content.get_exercises(course, assignment), exercise_statuses=content.get_exercise_statuses(course, assignment, self.get_user_info()["user_id"]), course_basics=content.get_course_basics(course), assignment_basics=assignment_basics, assignment_details=assignment_details, percentage_options=percentage_options, hour_options=hour_options, minute_options=minute_options, result=result, user_info=self.get_user_info())

        except Exception as inst:
            render_error(self, traceback.format_exc())

