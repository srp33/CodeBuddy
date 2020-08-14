from helper import *
from content import *
import contextvars
import json
import logging
import re
import sys
import tornado.ioloop
from tornado.log import enable_pretty_logging
from tornado.log import LogFormatter
from tornado.options import options
from tornado.options import parse_command_line
from tornado.web import *
import traceback
from urllib.parse import urlencode
import urllib.request
import uuid
import sqlite3
from sqlite3 import Error
import html

def make_app():
    app = Application([
        url(r"/", HomeHandler),
        url(r"\/course\/([^\/]+)", CourseHandler, name="course"),
        url(r"\/edit_course\/([^\/]+)?", EditCourseHandler, name="edit_course"),
        url(r"\/delete_course\/([^\/]+)?", DeleteCourseHandler, name="delete_course"),
        url(r"\/delete_course_submissions\/([^\/]+)?", DeleteCourseSubmissionsHandler, name="delete_course_submissions"),
        url(r"\/import_course", ImportCourseHandler, name="import_course"),
        url(r"\/export_course\/([^\/]+)?", ExportCourseHandler, name="export_course"),
        url(r"\/assignment\/([^\/]+)\/([^\/]+)", AssignmentHandler, name="assignment"),
        url(r"\/edit_assignment\/([^\/]+)\/([^\/]+)?", EditAssignmentHandler, name="edit_assignment"),
        url(r"\/delete_assignment\/([^\/]+)\/([^\/]+)?", DeleteAssignmentHandler, name="delete_assignment"),
        url(r"\/delete_assignment_submissions\/([^\/]+)\/([^\/]+)?", DeleteAssignmentSubmissionsHandler, name="delete_assignment_submissions"),
        url(r"\/problem\/([^\/]+)\/([^\/]+)/([^\/]+)", ProblemHandler, name="problem"),
        url(r"\/edit_problem\/([^\/]+)\/([^\/]+)/([^\/]+)?", EditProblemHandler, name="edit_problem"),
        url(r"\/delete_problem\/([^\/]+)\/([^\/]+)/([^\/]+)?", DeleteProblemHandler, name="delete_problem"),
        url(r"\/delete_problem_submissions\/([^\/]+)\/([^\/]+)/([^\/]+)?", DeleteProblemSubmissionsHandler, name="delete_problem_submissions"),
        url(r"\/run_code\/([^\/]+)\/([^\/]+)/([^\/]+)", RunCodeHandler, name="run_code"),
        url(r"\/submit\/([^\/]+)\/([^\/]+)/([^\/]+)", SubmitHandler, name="submit"),
        url(r"\/get_submission\/([^\/]+)\/([^\/]+)/([^\/]+)/(\d+)", GetSubmissionHandler, name="get_submission"),
        url(r"\/get_submissions\/([^\/]+)\/([^\/]+)/([^\/]+)/([^\/]+)", GetSubmissionsHandler, name="get_submissions"),
        url(r"\/view_answer\/([^\/]+)\/([^\/]+)/([^\/]+)", ViewAnswerHandler, name="view_answer"),
        url(r"\/add_admin", AddAdminHandler, name="add_admin"),
        url(r"\/add_instructor\/([^\/]+)", AddInstructorHandler, name="add_instructor"),
        url(r"\/add_assistant\/([^\/]+)", AddAssistantHandler, name="add_assistant"),
        url(r"\/student_submissions", StudentSubmissionsHandler, name="student_submissions"),
        url(r"\/student_problem\/([^\/]+)\/([^\/]+)/([^\/]+)/([^\/]+)", StudentProblemHandler, name="student_problem"),
        url(r"\/back_end\/([^\/]+)", BackEndHandler, name="back_end"),
        url(r"/static/(.+)", StaticFileHandler, name="static_file"),
        url(r"\/summarize_logs", SummarizeLogsHandler, name="summarize_logs"),
        url(r"/login(/.+)", LoginHandler, name="login"),
        url(r"/logout", LogoutHandler, name="logout"),
    ], autoescape=None)

        #url(r"/data/([^\/]+)\/([^\/]+)/([^\/]+)/(.+)", DataHandler, name="data"),

    return app

class HomeHandler(RequestHandler):
    def prepare(self):
        raw_current_user_id = self.get_secure_cookie("user_id")

        # Set context variables depending on whether the user is logged in.
        if raw_current_user_id:
            user_id_var.set(raw_current_user_id.decode())
            user_logged_in_var.set(True)

        else:
            user_id_var.set(self.request.remote_ip)
            user_logged_in_var.set(False)

    def get(self):
        try:
            self.render("home.html", courses=content.get_courses(show_hidden(self)), user_id=user_id_var.get(), role=content.get_role(user_id_var.get()), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class BaseUserHandler(RequestHandler):
    def prepare(self):
        user_id = self.get_secure_cookie("user_id")

        if user_id:
            user_id_var.set(user_id.decode())
            user_logged_in_var.set(True)
        else:
            user_id_var.set(self.request.remote_ip)
            user_logged_in_var.set(False)

            self.redirect("/login{}".format(self.request.path))

    def get_current_user(self):
        return user_id_var.get()

class CourseHandler(BaseUserHandler):
    def get(self, course):
        try:
            user_id = self.get_current_user()
            show = show_hidden(self)
            self.render("course.html", courses=content.get_courses(show), assignments=content.get_assignments(course, show), course_basics=content.get_course_basics(course), course_details=content.get_course_details(course, True), user_id=user_id, user_logged_in=user_logged_in_var.get(), role=content.get_role(user_id))
        except Exception as inst:
            render_error(self, traceback.format_exc())

class EditCourseHandler(BaseUserHandler):
    def get(self, course):
        user_id = self.get_current_user()
        role = content.get_role(user_id)
        if role == "administrator" or role == "instructor":
            try:
                self.render("edit_course.html", courses=content.get_courses(), assignments=content.get_assignments(course), course_basics=content.get_course_basics(course), course_details=content.get_course_details(course), result=None, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            try:
                self.render("permissions.html")
            except Exception as inst:
                render_error(self, traceback.format_exc())

    def post(self, course):
        try:
            title = self.get_body_argument("title").strip()
            visible = self.get_body_argument("is_visible") == "Yes"
            introduction = self.get_body_argument("introduction").strip()

            course_basics = content.get_course_basics(course)
            course_details = content.get_course_details(course)
            result = "Success: Course information saved!"

            if title == "" or introduction == "":
                result = "Error: Missing title or introduction."
            else:
                if content.has_duplicate_title(content.get_courses(), course, title):
                    result = "Error: A course with that title already exists."
                else:
                    if re.search(r"[^\w ]", title):
                        result = "Error: The title can only contain alphanumeric characters and spaces."
                    else:
                        course_basics["title"] = title
                        course_basics["visible"] = visible
                        course_details["introduction"] = introduction

                        content.save_course(course_basics, course_details)
                        course_basics["exists"] = True

            self.render("edit_course.html", courses=content.get_courses(), assignments=content.get_assignments(course), course_basics=content.get_course_basics(course), course_details=course_details, result=result, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DeleteCourseHandler(BaseUserHandler):
    def get(self, course):   
        user_id = self.get_current_user()
        role = content.get_role(user_id)
        if role == "administrator":
            try:
                self.render("delete_course.html", courses=content.get_courses(), assignments=content.get_assignments(course), course_basics=content.get_course_basics(course), result=None, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            try: 
                self.render("permissions.html")
            except Exception as inst:
                render_error(self, traceback.format_exc())

    def post(self, course):
        try:
            content.delete_course(content.get_course_basics(course))
            result = "Success: Course deleted."

            self.render("delete_course.html", courses=content.get_courses(), assignments=content.get_assignments(course), course_basics=content.get_course_basics(course), result=result, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DeleteCourseSubmissionsHandler(BaseUserHandler):
    def get(self, course):
        user_id = self.get_current_user()
        role = content.get_role(user_id)
        if role == "administrator" or role == "instructor":
            try:
                self.render("delete_course_submissions.html", courses=content.get_courses(), assignments=content.get_assignments(course), course_basics=content.get_course_basics(course), result=None, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            except Exception as inst:
                render_error(self, traceback.format_exc())

    def post(self, course):
        try:
            content.delete_course_submissions(content.get_course_basics(course))
            result = "Success: Course submissions deleted."

            self.render("delete_course_submissions.html", courses=content.get_courses(), assignments=content.get_assignments(course), course_basics=content.get_course_basics(course), result=result, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ImportCourseHandler(BaseUserHandler):
    def get(self):    
        user_id = self.get_current_user()
        role = content.get_role(user_id)
        if role == "administrator":
            try:
                self.render("import_course.html", result=None, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            try: 
                self.render("permissions.html")
            except Exception as inst:
                render_error(self, traceback.format_exc())

    def post(self):
        try:
            result = ""
            if self.request.files["zip_file"][0]["content_type"] == 'application/zip':
                zip_file_name = self.request.files["zip_file"][0]["filename"]
                zip_file_contents = self.request.files["zip_file"][0]["body"]

                import io
                import zipfile
                zip_data = BytesIO()
                zip_data.write(zip_file_contents)
                zip_file = zipfile.ZipFile(zip_data)
                version = int(zip_file.read("VERSION"))

                for file_path in zip_file.namelist():
                    file_info = zip_file.getinfo(file_path)

                    # Prevent the use of absolute paths within the zip file.
                    # Ignore directories and VERSION file.
                    if file_path.startswith("/") or file_info.is_dir() or file_path == "VERSION":
                        continue

                    out_path = "{}/{}".format(get_root_dir_path(), file_info.filename)

                    if os.path.exists(out_path):
                        result = "Error: A file or directory called {} already exists, so this import is not allowed. This course must first be deleted if you want to import.".format(out_path)
                        break

                    os.makedirs(os.path.dirname(out_path), exist_ok=True)
                    with open(out_path, 'wb') as out_file:
                        out_file.write(zip_file.read(file_path))

                if not result.startswith("Error:"):
                    result = "Success: The course was imported!"
            else:
                result = "Error: The uploaded file was not recognized as a zip file."

            self.render("import_course.html", result=result, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ExportCourseHandler(BaseUserHandler):
    def get(self, course):
        user_id = self.get_current_user()
        role = content.get_role(user_id)
        if role == "administrator":
            try:
                temp_dir_path = "/tmp/{}".format(create_id())
                zip_file_name = "{}.zip".format(content.get_course_basics(course)["title"].replace(" ", "_"))
                zip_file_path = "{}/{}".format(temp_dir_path, zip_file_name)

                os.makedirs(temp_dir_path)

                os.system("cp -r {} {}/".format(get_course_dir_path(course), temp_dir_path))
                os.system("cp VERSION {}/".format(temp_dir_path))
                os.system("cd {}; zip -r -qq {} .".format(temp_dir_path, zip_file_path))

                zip_bytes = read_file(zip_file_path, "rb")

                self.set_header('Content-type', 'application/zip')
                self.set_header('Content-Disposition', 'attachment; filename=' + zip_file_name)
                self.write(zip_bytes)
                self.finish()
                os.remove(zip_file_path)
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            try: 
                self.render("permissions.html")
            except Exception as inst:
                render_error(self, traceback.format_exc())

class AssignmentHandler(BaseUserHandler):
    def get(self, course, assignment):
        user_id = self.get_current_user()
        role = content.get_role(user_id)
        if role == "administrator" or role == "instructor" or role == "assistant":
            try:
                show = show_hidden(self)
                self.render("assignment_admin.html", courses=content.get_courses(show), assignments=content.get_assignments(course, show), problems=content.get_problems(course, assignment, show), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), assignment_details=content.get_assignment_details(course, assignment, True), user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            try:
                show = show_hidden(self)
                course_basics=content.get_course_basics(course)
                self.render("assignment.html", courses=content.get_courses(show), assignments=content.get_assignments(course, show), problem_statuses=content.get_problem_statuses(user_id, course, assignment), course_basics=course_basics, assignment_basics=content.get_assignment_basics(course, assignment), assignment_details=content.get_assignment_details(course, assignment, True), user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            except Exception as inst:
                render_error(self, traceback.format_exc())

class EditAssignmentHandler(BaseUserHandler):
    def get(self, course, assignment):
        user_id = self.get_current_user()
        role = content.get_role(user_id)
        if role == "administrator" or role == "instructor" or role == "assistant":
            try:
                self.render("edit_assignment.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=content.get_problems(course, assignment), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), assignment_details=content.get_assignment_details(course, assignment), result=None, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            try: 
                self.render("permissions.html")
            except Exception as inst:
                render_error(self, traceback.format_exc())

    def post(self, course, assignment):
        try:
            title = self.get_body_argument("title").strip()
            visible = self.get_body_argument("is_visible") == "Yes"
            introduction = self.get_body_argument("introduction").strip()

            assignment_basics = content.get_assignment_basics(course, assignment)
            assignment_details = content.get_assignment_details(course, assignment)
            result = "Success: Assignment information saved!"

            if title == "" or introduction == "":
                result = "Error: Missing title or introduction."
            else:
                if content.has_duplicate_title(content.get_assignments(course), assignment, title):
                    result = "Error: An assignment with that title already exists."
                else:
                    assignment_basics["title"] = title
                    assignment_basics["visible"] = visible
                    assignment_details["introduction"] = introduction

                    content.save_assignment(course, assignment_basics, assignment_details)
                    assignment_basics["exists"] = True

            self.render("edit_assignment.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=content.get_problems(course, assignment), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), assignment_details=assignment_details, result=result, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DeleteAssignmentHandler(BaseUserHandler):
    def get(self, course, assignment):
        user_id = self.get_current_user()
        role = content.get_role(user_id)
        if role == "administrator" or role == "instructor":
            try:
                self.render("delete_assignment.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=content.get_problems(course, assignment), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), result=None, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            try: 
                self.render("permissions.html")
            except Exception as inst:
                render_error(self, traceback.format_exc())

    def post(self, course, assignment):
        try:
            content.delete_assignment(content.get_assignment_basics(course, assignment))
            result = "Success: Assignment deleted."

            self.render("delete_assignment.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=content.get_problems(course, assignment), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), result=result, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DeleteAssignmentSubmissionsHandler(BaseUserHandler):
    def get(self, course, assignment):
        user_id = self.get_current_user()
        role = content.get_role(user_id)
        if role == "administrator" or role == "instructor":
            try:
                self.render("delete_assignment_submissions.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=content.get_problems(course, assignment), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), result=None, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            try: 
                self.render("permissions.html")
            except Exception as inst:
                render_error(self, traceback.format_exc())

    def post(self, course, assignment):
        try:
            content.delete_assignment_submissions(content.get_assignment_basics(course, assignment))
            result = "Success: Assignment submissions deleted."

            self.render("delete_assignment_submissions.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=content.get_problems(course, assignment), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), result=result, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ProblemHandler(BaseUserHandler):
    def get(self, course, assignment, problem):
        try:
            user = self.get_current_user()
            show = show_hidden(self)
            problems = content.get_problems(course, assignment, show)
            problem_details = content.get_problem_details(course, assignment, problem, format_content=True)
            back_end = settings_dict["back_ends"][problem_details["back_end"]]

            self.render("problem.html", courses=content.get_courses(show), assignments=content.get_assignments(course, show), problems=problems, course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), problem_basics=content.get_problem_basics(course, assignment, problem), problem_details=problem_details, next_prev_problems=content.get_next_prev_problems(course, assignment, problem, problems), code_completion_path=back_end["code_completion_path"], back_end_description=back_end["description"], num_submissions=content.get_num_submissions(course, assignment, problem, user), user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get(), role=content.get_role(user))

        except Exception as inst:
            render_error(self, traceback.format_exc())

class EditProblemHandler(BaseUserHandler):
    def get(self, course, assignment, problem):
        user_id = self.get_current_user()
        role = content.get_role(user_id)
        if role == "administrator" or role == "instructor":
            try:
                problems = content.get_problems(course, assignment)
                problem_details = content.get_problem_details(course, assignment, problem)
                self.render("edit_problem.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=problems, course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), problem_basics=content.get_problem_basics(course, assignment, problem), problem_details=problem_details, next_prev_problems=content.get_next_prev_problems(course, assignment, problem, problems), code_completion_path=settings_dict["back_ends"][problem_details["back_end"]]["code_completion_path"], back_ends=sort_nicely(settings_dict["back_ends"].keys()), result=None, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            try: 
                self.render("permissions.html")
            except Exception as inst:
                render_error(self, traceback.format_exc())

    def post(self, course, assignment, problem):
        try:
            title = self.get_body_argument("title").strip() #required
            visible = self.get_body_argument("is_visible") == "Yes"
            instructions = self.get_body_argument("instructions").strip().replace("\r", "") #required
            back_end = self.get_body_argument("back_end")
            output_type = self.get_body_argument("output_type")
            answer_code = self.get_body_argument("answer_code_text").strip().replace("\r", "") #required
            answer_description = self.get_body_argument("answer_description").strip().replace("\r", "")
            test_code = self.get_body_argument("test_code_text").strip().replace("\r", "")
            credit = self.get_body_argument("credit").strip().replace("\r", "")
            data_url = self.get_body_argument("data_url").strip().replace("\r", "")
            data_file_name = self.get_body_argument("data_file_name").strip().replace("\r", "")
            show_expected = self.get_body_argument("show_expected") == "Yes"
            show_test_code = self.get_body_argument("show_test_code") == "Yes"
            show_answer = self.get_body_argument("show_answer") == "Yes"

            problem_basics = content.get_problem_basics(course, assignment, problem)
            problem_details = content.get_problem_details(course, assignment, problem)
            result = "Success: The problem was saved!"

            if title == "" or instructions == "" or answer_code == "":
                result = "Error: One of the required fields is missing."
            else:
                if content.has_duplicate_title(content.get_problems(course, assignment), problem, title):
                    result = "Error: A problem with that title already exists in this assignment."
                else:
                    if (data_url == "" and data_file_name != "") or (data_url != "" and data_file_name == ""):
                        result = "Error: If a data URL or file name is specified, both must be specified."
                    else:
                        if data_url == "":
                            data_contents = b""
                        else:
                            if not data_file_name in instructions:
                                result = f"Error: You must mention {data_file_name} at least once in the instructions."
                            else:
                                data_contents = download_file(data_url)

                                # Make sure the file is not larger than 10 MB.
                                if len(data_contents) > 10 * 1024 * 1024:
                                    result = f"Error: The file at {data_url} is too large ({len(data_contents)} bytes)."

                        if not result.startswith("Error:"):
                            problem_basics["title"] = title
                            problem_basics["visible"] = visible

                            problem_details["instructions"] = instructions
                            problem_details["back_end"] = back_end
                            problem_details["output_type"] = output_type
                            problem_details["answer_code"] = answer_code
                            problem_details["answer_description"] = answer_description
                            problem_details["test_code"] = test_code
                            problem_details["credit"] = credit
                            problem_details["data_url"] = data_url
                            problem_details["data_file_name"] = data_file_name
                            problem_details["data_contents"] = data_contents.decode()
                            problem_details["show_expected"] = show_expected
                            problem_details["show_test_code"] = show_test_code
                            problem_details["show_answer"] = show_answer

                            expected_output, error_occurred = exec_code(settings_dict["back_ends"][problem_details["back_end"]], answer_code, problem_basics, problem_details)

                            if error_occurred:
                                result = "Error: " + expected_output
                            else:
                                problem_details["expected_output"] = expected_output
                                content.save_problem(course, assignment, problem_basics, problem_details)
                                problem_basics["exists"] = True

            problems = content.get_problems(course, assignment)
            self.render("edit_problem.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=problems, course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), problem_basics=problem_basics, problem_details=problem_details, next_prev_problems=content.get_next_prev_problems(course, assignment, problem, problems), code_completion_path=settings_dict["back_ends"][problem_details["back_end"]]["code_completion_path"], back_ends=sort_nicely(settings_dict["back_ends"].keys()), result=result, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
        except ConnectionError as inst:
            render_error(self, "The front-end server was unable to contact the back-end server to check your code.")
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DeleteProblemHandler(BaseUserHandler):
    def get(self, course, assignment, problem):
        user_id = self.get_current_user()
        role = content.get_role(user_id)
        if role == "administrator" or role == "instructor":
            try:
                problems = content.get_problems(course, assignment)
                self.render("delete_problem.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=problems, course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), problem_basics=content.get_problem_basics(course, assignment, problem), next_prev_problems=content.get_next_prev_problems(course, assignment, problem, problems), result=None, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            try: 
                self.render("permissions.html")
            except Exception as inst:
                render_error(self, traceback.format_exc())

    def post(self, course, assignment, problem):
        try:
            content.delete_problem(content.get_problem_basics(course, assignment, problem))
            result = "Success: Problem deleted."

            problems =content.get_problems(course, assignment)
            self.render("delete_problem.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=problems, course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), problem_basics=content.get_problem_basics(course, assignment, problem), next_prev_problems=content.get_next_prev_problems(course, assignment, problem, problems), result=result, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DeleteProblemSubmissionsHandler(BaseUserHandler):
    def get(self, course, assignment, problem):
        user_id = self.get_current_user()
        role = content.get_role(user_id)
        if role == "administrator" or role == "instructor":
            try:
                problems =content.get_problems(course, assignment)
                self.render("delete_problem_submissions.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=problems, course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), problem_basics=content.get_problem_basics(course, assignment, problem), next_prev_problems=content.get_next_prev_problems(course, assignment, problem, problems), result=None, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            try: 
                self.render("permissions.html")
            except Exception as inst:
                render_error(self, traceback.format_exc())

    def post(self, course, assignment, problem):
        try:
            content.delete_problem_submissions(content.get_problem_basics(course, assignment, problem))
            result = "Success: Problem submissions deleted."

            problems =content.get_problems(course, assignment)
            self.render("delete_problem_submissions.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=problems, course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), problem_basics=content.get_problem_basics(course, assignment, problem), next_prev_problems=content.get_next_prev_problems(course, assignment, problem, problems), result=result, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class RunCodeHandler(BaseUserHandler):
    async def post(self, course, assignment, problem):
        user = self.get_current_user()
        code = self.get_body_argument("user_code").replace("\r", "")

        problem_basics =content.get_problem_basics(course, assignment, problem)
        problem_details =content.get_problem_details(course, assignment, problem)

        out_dict = {"error_occurred": True}

        try:
            code_output, error_occurred = exec_code(settings_dict["back_ends"][problem_details["back_end"]], code, problem_basics, problem_details, request=None)

            if problem_details["output_type"] == "txt" or error_occurred:
                code_output = format_output_as_html(code_output)

            out_dict["code_output"] = code_output
            out_dict["error_occurred"] = error_occurred

        except Exception as inst:
            out_dict["code_output"] = format_output_as_html(traceback.format_exc())

        self.write(json.dumps(out_dict))

class SubmitHandler(BaseUserHandler):
    async def post(self, course, assignment, problem):
        user = self.get_current_user()
        code = self.get_body_argument("user_code").replace("\r", "")
        #date = self.get_body_argument("date")
        #date = re.sub(r"(\d*\/\d*)\/\d{4}(, \d*:\d*):\d*( .M)", r"\1\2\3", date) # To make date shorter, optional

        problem_basics = content.get_problem_basics(course, assignment, problem)
        problem_details = content.get_problem_details(course, assignment, problem)

        out_dict = {"error_occurred": True, "passed": False, "diff_output": "", "submission_id": ""}

        try:
            if problem_details["output_type"] == "txt":
                code_output, error_occurred, passed, diff_output = test_code_txt(settings_dict["back_ends"][problem_details["back_end"]], code, problem_basics, problem_details, self.request)
            else:
                code_output, error_occurred, passed, diff_output = test_code_jpg(settings_dict["back_ends"][problem_details["back_end"]], code, problem_basics, problem_details, self.request)

            if problem_details["output_type"] == "txt" or error_occurred:
                code_output = format_output_as_html(code_output)

            out_dict["code_output"] = code_output
            out_dict["error_occurred"] = error_occurred
            out_dict["passed"] = passed
            out_dict["diff_output"] = diff_output
            out_dict["submission_id"] = content.save_submission(course, assignment, problem, user, code, code_output, passed, error_occurred)
        except ConnectionError as inst:
            out_dict["code_output"] = "The front-end server was unable to contact the back-end server to check your code."
        except Exception as inst:
            out_dict["code_output"] = format_output_as_html(traceback.format_exc())

        self.write(json.dumps(out_dict))

class GetSubmissionHandler(BaseUserHandler):
    def get(self, course, assignment, problem, submission_id):
        try:
            user = self.get_current_user()
            problem_details = content.get_problem_details(course, assignment, problem)

            submission_info = content.get_submission_info(course, assignment, problem, user, submission_id)

            if submission_info["error_occurred"]:
                submission_info["diff_output"] = ""
            elif problem_details["output_type"] == "txt":
                submission_info["diff_output"] =  find_differences_txt(problem_details, submission_info["code_output"], submission_info["passed"])
            else:
                diff_percent, diff_image = diff_jpg(problem_details["expected_output"], submission_info["code_output"])
                submission_info["diff_output"] =  find_differences_jpg(problem_details, submission_info["passed"], diff_image)
                submission_info["code_output"] = format_output_as_html(submission_info["code_output"])

        except Exception as inst:
            submission_info["error_occurred"] = True
            submission_info["diff_output"] = ""
            submission_info["code_output"] = format_output_as_html(traceback.format_exc())

        self.write(json.dumps(submission_info))

class GetSubmissionsHandler(BaseUserHandler):
    def get(self, course, assignment, problem, user_id):
        try:
            #user = self.get_current_user()
            submissions = content.get_submissions_basic(course, assignment, problem, user_id)
        except Exception as inst:
            submissions = []

        self.write(json.dumps(submissions))

#class DataHandler(RequestHandler):
#    async def get(self, course, assignment, problem, file_name):
#        data_file_path = get_downloaded_file_path(file_name)
#
#        problem_details = content.get_problem_details(course, assignment, problem)
#
#        content_type = get_columns_dict(problem_details["data_urls_info"], 1, 2)[file_name]
#        self.set_header('Content-type', content_type)
#
#        if not os.path.exists(data_file_path) or is_old_file(data_file_path):
#            url = get_columns_dict(problem_details["data_urls_info"], 1, 0)[file_name]
#
#            ## Check to see whether the request came from the server or the user's computer
#            #this_host = self.request.headers.get("Host")
#            #referer = self.request.headers.get("Referer")
#            #referer_url_parts = urllib.parse.urlparse(referer)
#            #referer_host = referer_url_parts[1]
#            #referer_path = referer_url_parts[2]
#
#            #if referer_host == this_host and referer_path.startswith("/problem") and content_type.startswith("text/"):
#            #    self.write("Please wait while the file is downloaded...\n\n")
#
#            urllib.request.urlretrieve(url, data_file_path)
#
#        self.write(read_file(data_file_path))

class ViewAnswerHandler(BaseUserHandler):
    def get(self, course, assignment, problem):
        try:
            user = self.get_current_user()
            self.render("view_answer.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=content.get_problems(course, assignment), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), problem_basics=content.get_problem_basics(course, assignment, problem), problem_details=content.get_problem_details(course, assignment, problem), last_submission=content.get_last_submission(course, assignment, problem, user), format_content=True)
        except Exception as inst:
            render_error(self, traceback.format_exc())

class AddAdminHandler(BaseUserHandler):
    def get(self):
        user_id = self.get_current_user()
        role = content.get_role(user_id)
        if role == "administrator":
            try:
                self.render("add_admin.html", admins=content.get_users_from_role("administrator", None), attempt = False)
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            try: 
                self.render("permissions.html")
            except Exception as inst:
                render_error(self, traceback.format_exc())
    def post(self):
        try:
            new_admin = self.get_body_argument("new_admin")
            added = content.add_row_permissions(new_admin, "administrator", None)
            self.render("add_admin.html", admins=content.get_users_from_role("administrator", None), added=added, attempt = True)
        except Exception as inst:
            render_error(self, traceback.format_exc())

class AddInstructorHandler(BaseUserHandler):
    def get(self, course):
        user_id = self.get_current_user()
        role = content.get_role(user_id)
        if role == "administrator":
            try:
                course_basics = content.get_course_basics(course)
                self.render("add_instructor.html", courses=content.get_courses(), course_basics=course_basics, instructors=content.get_users_from_role("instructor", course_basics["id"]), attempt = False)
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            try: 
                self.render("permissions.html")
            except Exception as inst:
                render_error(self, traceback.format_exc())
    def post(self, course):
        try:
            course_basics = content.get_course_basics(course)
            new_instructor = self.get_body_argument("new_inst")
            added = content.add_row_permissions(new_instructor, "instructor", course_basics["id"])
            self.render("add_instructor.html", courses=content.get_courses(), course_basics=course_basics, instructors=content.get_users_from_role("instructor", course_basics["id"]), added=added, attempt = True)
        except Exception as inst:
            render_error(self, traceback.format_exc())

class AddAssistantHandler(BaseUserHandler):
    def get(self, course):
        user_id = self.get_current_user()
        role = content.get_role(user_id)
        if role == "instructor":
            try:
                course_basics = content.get_course_basics(course)
                self.render("add_assistant.html", courses=content.get_courses(), course_basics=course_basics, assistants=content.get_users_from_role("assistant", course_basics["id"]), attempt = False)
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            try: 
                self.render("permissions.html")
            except Exception as inst:
                render_error(self, traceback.format_exc())
    def post(self, course):
        try:
            course_basics = content.get_course_basics(course)
            new_assistant = self.get_body_argument("new_assistant")
            added = content.add_row_permissions(new_assistant, "assistant", course_basics["id"])
            self.render("add_assistant.html", courses=content.get_courses(), course_basics=course_basics, assistants=content.get_users_from_role("assistant", course_basics["id"]), added=added, attempt = True)
        except Exception as inst:
            render_error(self, traceback.format_exc()) 

class StudentSubmissionsHandler(BaseUserHandler):
#(This is just a filler html page to be able to access the instructor view of a student's problem, Emme's page will replace it)
    def get(self):
        try:
            student_id = "ajohns58"
            self.render("student_submissions.html", student_id="ajohns58", courses=content.get_courses(), course_dict=content.course_ids_to_titles(), assignment_dict=content.assignment_ids_to_titles(), problem_dict=content.problem_ids_to_titles(), student_courses=content.get_student_courses(student_id), student_assignments=content.get_student_assignments(student_id), student_problems=content.get_student_problems(student_id), num_submissions=content.get_user_total_submissions(student_id))
        except Exception as inst:
            render_error(self, traceback.format_exc())

class StudentProblemHandler(BaseUserHandler):
    def get(self, course, assignment, problem, student_id):
        try:
            show = show_hidden(self)
            problems = content.get_problems(course, assignment, show)
            problem_details = content.get_problem_details(course, assignment, problem, format_content=True)
            back_end = settings_dict["back_ends"][problem_details["back_end"]]
            self.render("student_problem.html", user_id="ajohns58", student_id="ajohns58", courses=content.get_courses(show), assignments=content.get_assignments(course, show), problems=problems, course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), problem_basics=content.get_problem_basics(course, assignment, problem), problem_details=problem_details, next_prev_problems=content.get_next_prev_problems(course, assignment, problem, problems), code_completion_path=back_end["code_completion_path"], back_end_description=back_end["description"], num_submissions=content.get_num_submissions(course, assignment, problem, student_id), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class BackEndHandler(RequestHandler):
    def get(self, back_end):
        try:
            self.write(json.dumps(settings_dict["back_ends"][back_end]))
        except Exception as inst:
            logging.error(self, traceback.format_exc())
            self.write(json.dumps({"Error": "An error occurred."}))

class SummarizeLogsHandler(RequestHandler):
    def get(self):
        user_id = self.get_current_user()
        role = content.get_role(user_id)
        if role == "administrator":
            try:
                years, months, days = get_list_of_dates()
                self.render("summarize_logs.html", filter_list = sorted(content.get_root_dirs_to_log()), years=years, months=months, days=days, show_table = False)
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            try: 
                self.render("permissions.html")
            except Exception as inst:
                render_error(self, traceback.format_exc())

    def post(self):
        try:
            filter = self.get_body_argument("filter_select")
            year = self.get_body_argument("year_select")
            if year != "No filter":
                year = year[2:]
            month = self.get_body_argument("month_select")
            day = self.get_body_argument("day_select")
            log_file = self.get_body_argument("file_select")
            if log_file == "Select file":
                log_file = "logs/summarized/HitsAnyUser.tsv.gz"
            years, months, days = get_list_of_dates()

            self.render("summarize_logs.html", filter = filter, filter_list = sorted(content.get_root_dirs_to_log()), years=years, months=months, days=days, log_dict = content.get_log_table_contents(log_file, year, month, day), show_table = True)
        except Exception as inst:
            render_error(self, traceback.format_exc())

class StaticFileHandler(RequestHandler):
    async def get(self, file_name):
        file_path = f"/static/{file_name}"

        if file_name.endswith(".html"):
            self.render(file_path, user_logged_in=False)
        else:
            content_type = "text/css"
            read_mode = "r"

            if file_name.endswith(".js"):
                content_type = "text/javascript"
            elif file_name.endswith(".png"):
                content_type = "image/png"
                read_mode = "rb"
            elif file_name.endswith(".ico"):
                content_type = "image/x-icon"
                read_mode = "rb"
            elif file_name.endswith(".webmanifest"):
                content_type = "application/json"

            file_contents = read_file("/static/{}".format(file_name), mode=read_mode)

            self.set_header('Content-type', content_type)
            self.write(file_contents)

class LoginHandler(RequestHandler):
    async def get(self, target_path):
        self.render("login.html", courses=content.get_courses(show_hidden(self)), target_path=target_path)

    def post(self, target_path):
        try:
            user_id = self.get_body_argument("user_id")

            if user_id == "":
                self.write("Invalid user ID.")
            else:
                if not content.check_user_exists(user_id):
                    content.add_user(user_id)
                    #print("Users:", content.print_rows("users"))

                if content.check_role_exists(user_id):
                    role = content.get_role(user_id)
                    #print("This is the current user's role: ", role)
                else:
                    content.add_row_permissions(user_id, "administrator", None)
                    #print("Permissions:", content.print_rows("permissions"))

                self.set_secure_cookie("user_id", user_id, expires_days=30)
                self.redirect(target_path)
        except Exception as inst:
            render_error(self, traceback.format_exc())

class LogoutHandler(BaseUserHandler):
    def get(self):
        self.write(self.get_current_user())
        self.clear_cookie("user_id")
        self.redirect("/")

#from tornado.auth import GoogleOAuth2Mixin
#class LoginHandler(BaseUserHandler, GoogleOAuth2Mixin):
#    async def get(self):
#        if self.get_argument("code", None):
#            authorization_code = self.get_argument("code", None)
#            self.get_authenticated_user(authorization_code, self.async_callback(self._on_auth))
#            return
#        self.authorize_redirect(self.settings['google_permissions'])
#
#    def _on_auth(self, response):
#        print(response.body)
#        print(response.request.headers)
#        if response.error:
#            raise tornado.web.HTTPError(500, "Google auth failed")
#        #self.set_secure_cookie("user_id", tornado.escape.json_encode(user))
#        #self.redirect("/")
#
#from tornado.auth import GoogleOAuth2Mixin
#class GoogleOAuth2LoginHandler(BaseUserHandler, GoogleOAuth2Mixin):
#    async def get(self):
#        if self.get_argument('code', False):
#            user = await self.get_authenticated_user(
#                redirect_uri='http://your.site.com/auth/google',
#                code=self.get_argument('code'))
#
#            if not self.get_secure_cookie("user"):
#                self.set_secure_cookie("user", user, expires_days=30)
#                self.write("Your cookie was not set yet!")
#        else:
#            await self.authorize_redirect(
#                redirect_uri='http://your.site.com/auth/google',
#                client_id=self.settings['google_oauth']['key'],
#                scope=['profile', 'email'],
#                response_type='code',
#                extra_params={'approval_prompt': 'auto'})

# See https://quanttype.net/posts/2020-02-05-request-id-logging.html
class LoggingFilter(logging.Filter):
    def filter(self, record):
        record.user_id = user_id_var.get("-")
        return True

if __name__ == "__main__":
    if "PORT" in os.environ and "MPORT" in os.environ:
        application = make_app()

        content = Content()
        content.create_sqlite_tables()

        #TODO: Use something other than the password. Store in a file?
        application.settings["cookie_secret"] = "abc"
        settings_dict = get_settings()

        server = tornado.httpserver.HTTPServer(application)
        server.bind(int(os.environ['PORT']))
        server.start(int(os.environ['NUM_PROCESSES']))

        user_logged_in_var = contextvars.ContextVar("user_logged_in")
        user_id_var = contextvars.ContextVar("user_id")

        # Set up logging
        options.log_file_prefix = "/logs/codebuddy.log"
        options.log_file_max_size = 1024**2 * 1000 # 1 gigabyte per file
        options.log_file_num_backups = 10
        parse_command_line()
        my_log_formatter = LogFormatter(fmt='%(levelname)s %(asctime)s %(module)s %(message)s %(user_id)s')
        logging_filter = LoggingFilter()
        for handler in logging.getLogger().handlers:
            handler.addFilter(logging_filter)
        root_logger = logging.getLogger()
        root_streamhandler = root_logger.handlers[0]
        root_streamhandler.setFormatter(my_log_formatter)

        logging.info("Starting on port {}...".format(os.environ['PORT']))
        tornado.ioloop.IOLoop.instance().start()
    else:
        logging.error("Values must be specified for the PORT and MPORT environment variables.")
        sys.exit(1)
