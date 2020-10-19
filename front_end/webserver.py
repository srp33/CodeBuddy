from content import *
import contextvars
from datetime import datetime
from helper import *
import html
import io
import json
import logging
import re
import sys
from tornado.auth import GoogleOAuth2Mixin
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
import zipfile

def make_app():
    app = Application([
        url(r"/", HomeHandler),
        url(r"\/initialize", InitializeHandler, name="initialize"),
        url(r"\/course\/([^\/]+)", CourseHandler, name="course"),
        url(r"\/edit_course\/([^\/]+)?", EditCourseHandler, name="edit_course"),
        url(r"\/delete_course\/([^\/]+)?", DeleteCourseHandler, name="delete_course"),
        url(r"\/delete_course_submissions\/([^\/]+)?", DeleteCourseSubmissionsHandler, name="delete_course_submissions"),
        url(r"\/import_course", ImportCourseHandler, name="import_course"),
        url(r"\/export_course\/([^\/]+)?", ExportCourseHandler, name="export_course"),
        url(r"\/export_submissions\/([^\/]+)?", ExportSubmissionsHandler, name="export_submissions"),
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
        url(r"\/get_submission\/([^\/]+)\/([^\/]+)/([^\/]+)/([^\/]+)/(\d+)", GetSubmissionHandler, name="get_submission"),
        url(r"\/get_submissions\/([^\/]+)\/([^\/]+)/([^\/]+)/([^\/]+)", GetSubmissionsHandler, name="get_submissions"),
        url(r"\/view_answer\/([^\/]+)\/([^\/]+)/([^\/]+)", ViewAnswerHandler, name="view_answer"),
        url(r"\/add_admin", AddAdminHandler, name="add_admin"),
        url(r"\/add_instructor\/([^\/]+)", AddInstructorHandler, name="add_instructor"),
        url(r"\/add_assistant\/([^\/]+)", AddAssistantHandler, name="add_assistant"),
        url(r"\/remove_admin\/([^\/]+)", RemoveAdminHandler, name="remove_admin"),
        url(r"\/remove_instructor\/([^\/]+)\/([^\/]+)", RemoveInstructorHandler, name="remove_instructor"),
        url(r"\/remove_assistant\/([^\/]+)\/([^\/]+)", RemoveAssistantHandler, name="remove_assistant"),
        url(r"\/delete_user", DeleteUserHandler, name="delete_user"),
        url(r"\/view_scores\/([^\/]+)\/([^\/]+)", ViewScoresHandler, name="view_scores"),
        url(r"\/download_scores\/([^\/]+)\/([^\/]+)", DownloadScoresHandler, name="download_scores"),
        url(r"\/student_scores\/([^\/]+)\/([^\/]+)\/([^\/]+)", StudentScoresHandler, name="student_scores"),
        url(r"\/student_problem\/([^\/]+)\/([^\/]+)/([^\/]+)/([^\/]+)", StudentProblemHandler, name="student_problem"),
        url(r"\/back_end\/([^\/]+)", BackEndHandler, name="back_end"),
        url(r"/static/(.+)", StaticFileHandler, name="static_file"),
        url(r"\/summarize_logs", SummarizeLogsHandler, name="summarize_logs"),
        url(r"/login", GoogleLoginHandler, name="login"),
        url(r"/devlogin(/.+)?", DevelopmentLoginHandler, name="devlogin"),
        url(r"/logout", LogoutHandler, name="logout"),
    ], autoescape=None)

    return app

class HomeHandler(RequestHandler):
    def prepare(self):
        try:
            user_id = self.get_secure_cookie("user_id")

            # Set context variables depending on whether the user is logged in.
            if user_id:
                user_id = user_id.decode()
                user_id_var.set(user_id)
                user_logged_in_var.set(True)
                user_role_var.set(content.get_role(user_id))
            else:
                user_id_var.set(self.request.remote_ip)
                user_logged_in_var.set(False)
                user_role_var.set("not_logged_in")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def get(self):
        try:
            if content.check_administrator_exists():
                self.show_home_page()
            else:
                self.redirect("/initialize")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def show_home_page(self):
        self.render("home.html", courses=content.get_courses(show_hidden(user_role_var.get())), user_id=user_id_var.get(), role=user_role_var.get(), user_logged_in=user_logged_in_var.get())

class BaseUserHandler(RequestHandler):
    def prepare(self):
        try:
            user_id = self.get_secure_cookie("user_id")

            if user_id:
                user_id = user_id.decode()
                user_id_var.set(user_id)
                user_logged_in_var.set(True)
                user_role_var.set(content.get_role(user_id))
            else:
                user_id_var.set(self.request.remote_ip)
                user_logged_in_var.set(False)
                user_role_var.set("not_logged_in")

                if settings_dict["mode"] == "production":
                    self.set_secure_cookie("redirect_path", self.request.path)
                    self.redirect("/login")
                else:
                    self.redirect("/devlogin{}".format(self.request.path))
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def get_current_user(self):
        return user_id_var.get()

    def get_current_role(self):
        return user_role_var.get()

class InitializeHandler(BaseUserHandler):
    def get(self):
        try:
            if content.get_user_count() == 0:
                self.redirect("/login")
            else:
                content.add_admin_permissions(self.get_current_user())
                self.render("initialize.html", user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class CourseHandler(BaseUserHandler):
    def get(self, course):
        role = self.get_current_role()
        if role == "administrator" or role == "instructor" or role == "assistant":
            try:
                show = show_hidden(self)
                self.render("course_admin.html", courses=content.get_courses(show), assignments=content.get_assignments(course, True), course_basics=content.get_course_basics(course), course_details=content.get_course_details(course, True), course_scores=content.get_course_scores(course), user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get(), role=self.get_current_role())
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            try:
                show = show_hidden(self)
                user_id = self.get_current_user()
                self.render("course.html", courses=content.get_courses(show), assignments=content.get_assignments(course, show), assignment_statuses=content.get_assignment_statuses(course, user_id), course_basics=content.get_course_basics(course), course_details=content.get_course_details(course, True), user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get())
            except Exception as inst:
                render_error(self, traceback.format_exc())

class EditCourseHandler(BaseUserHandler):
    def get(self, course):
        try:
            role = self.get_current_role()
            if role == "administrator" or role == "instructor":
                self.render("edit_course.html", courses=content.get_courses(), assignments=content.get_assignments(course), course_basics=content.get_course_basics(course), course_details=content.get_course_details(course), result=None, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            else:
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course):
        try:
            role = self.get_current_role()
            if role != "administrator" and role != "instructor":
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
                return

            title = self.get_body_argument("title").strip()
            visible = self.get_body_argument("is_visible") == "Yes"
            introduction = self.get_body_argument("introduction").strip()

            course_basics = content.get_course_basics(course)
            course_details = content.get_course_details(course)
            result = "Success: Course information saved!"

            if title == "" or introduction == "":
                result = "Error: Missing title or introduction."
            else:
                if content.has_duplicate_title(content.get_courses(), course_basics["id"], title):
                    result = "Error: A course with that title already exists."
                else:
                    if re.search(r"[^\w ]", title):
                        result = "Error: The title can only contain alphanumeric characters and spaces."
                    else:
                        if len(title) > 20:
                            result = "Error: The title cannot exceed 20 characters."
                        else:
                            content.specify_course_basics(course_basics, title, visible)
                            content.specify_course_details(course_details, introduction, None, datetime.datetime.now())
                            course = content.save_course(course_basics, course_details)

            self.render("edit_course.html", courses=content.get_courses(), assignments=content.get_assignments(course), course_basics=content.get_course_basics(course), course_details=course_details, result=result, user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DeleteCourseHandler(BaseUserHandler):
    def get(self, course):
        try:
            if self.get_current_role() == "administrator":
                self.render("delete_course.html", courses=content.get_courses(), course_basics=content.get_course_basics(course), result=None, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            else:
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course):
        try:
            if self.get_current_role() != "administrator":
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
                return

            content.delete_course(content.get_course_basics(course))
            result = "Success: Course deleted."

            self.render("delete_course.html", courses=content.get_courses(), course_basics=content.get_course_basics(None), result=result, user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DeleteCourseSubmissionsHandler(BaseUserHandler):
    def get(self, course):
        try:
            role = self.get_current_role()
            if role == "administrator" or role == "instructor":
                self.render("delete_course_submissions.html", courses=content.get_courses(), course_basics=content.get_course_basics(course), result=None, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            else:
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course):
        try:
            role = self.get_current_role()
            if role != "administrator" and role != "instructor":
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
                return

            content.delete_course_submissions(content.get_course_basics(course))
            result = "Success: Course submissions deleted."

            self.render("delete_course_submissions.html", courses=content.get_courses(), course_basics=content.get_course_basics(course), result=result, user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ImportCourseHandler(BaseUserHandler):
    def get(self):
        try:
            if self.get_current_role() == "administrator":
                self.render("import_course.html", result=None, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            else:
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self):
        try:
            if self.get_current_role() != "administrator":
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
                return

            result = ""
            if "zip_file" in self.request.files and self.request.files["zip_file"][0]["content_type"] == 'application/zip':
                zip_file_name = self.request.files["zip_file"][0]["filename"]
                zip_file_contents = self.request.files["zip_file"][0]["body"]
                descriptor = zip_file_name.replace(".zip", "")

                zip_data = BytesIO()
                zip_data.write(zip_file_contents)
                zip_file = zipfile.ZipFile(zip_data)
                version = int(zip_file.read(f"{descriptor}/VERSION"))

                course_list = json.loads(zip_file.read(f"{descriptor}/courses.json"))[0]
                course_id = None
                course_basics = content.get_course_basics(course_id)
                content.specify_course_basics(course_basics, course_list[1], bool(course_list[3]))

                # Check whether course already exists.
                if content.has_duplicate_title(content.get_courses(), course_basics["id"], course_list[1]):
                    result = f"Error: A course with that title already exists."
                else:
                    course_details = content.get_course_details(course_id)
                    content.specify_course_details(course_details, course_list[2], convert_string_to_date(course_list[4]), convert_string_to_date(course_list[5]))
                    content.save_course(course_basics, course_details)

                    assignment_id_dict = {}
                    assignment_lists = json.loads(zip_file.read(f"{descriptor}/assignments.json"))
                    for assignment_list in assignment_lists:
                        assignment_id = None
                        assignment_basics = content.get_assignment_basics(course_basics["id"], assignment_id)
                        assignment_details = content.get_assignment_details(course_basics["id"], assignment_id)

                        content.specify_assignment_basics(assignment_basics, assignment_list[2], bool(assignment_list[4]))
                        #content.specify_assignment_details(assignment_details, assignment_list[3], convert_string_to_date(assignment_list[5]), convert_string_to_date(assignment_list[6]))

                        content.save_assignment(assignment_basics, assignment_details)
                        assignment_id_dict[assignment_list[1]] = assignment_basics["id"]

                    problem_lists = json.loads(zip_file.read(f"{descriptor}/problems.json"))
                    for problem_list in problem_lists:
                        problem_id = None
                        problem_basics = content.get_problem_basics(course_basics["id"], assignment_id_dict[problem_list[1]], problem_id)
                        problem_details = content.get_problem_details(course_basics["id"], assignment_id_dict[problem_list[1]], problem_id)

                        content.specify_problem_basics(problem_basics, problem_list[3], bool(problem_list[4]))

                        answer_code = problem_list[5]
                        answer_description = problem_list[6]
                        max_submissions = int(problem_list[7])
                        credit = problem_list[8]
                        data_url = problem_list[9]
                        data_file_name = problem_list[10]
                        data_contents = problem_list[11]
                        back_end = problem_list[12]
                        expected_output = problem_list[13]
                        instructions = problem_list[14]
                        output_type = problem_list[15]
                        show_answer = bool(problem_list[16])
                        show_expected = bool(problem_list[17])
                        show_test_code = bool(problem_list[18])
                        test_code = problem_list[19]
                        date_created = convert_string_to_date(problem_list[20])
                        date_updated = convert_string_to_date(problem_list[21])

                        content.specify_problem_details(problem_details, instructions, back_end, output_type, answer_code, answer_description, max_submissions, test_code, credit, data_url, data_file_name, data_contents, show_expected, show_test_code, show_answer, expected_output, date_created, date_updated)
                        content.save_problem(problem_basics, problem_details)

                    result = "Success: The course was imported!"
            else:
                result = "Error: The uploaded file was not recognized as a zip file."

            self.render("import_course.html", result=result, user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ExportCourseHandler(BaseUserHandler):
    def get(self, course):
        course_basics = content.get_course_basics(course)

        descriptor = f"Course_{course_basics['title'].replace(' ', '_')}"
        temp_dir_path, zip_file_name, zip_file_path = content.create_zip_file_path(descriptor)

        try:
            content.create_export_paths(temp_dir_path, descriptor)

            for table_name in ["courses", "assignments", "problems"]:
                content.export_data(course_basics, table_name, f"{temp_dir_path}/{descriptor}/{table_name}.json")

            content.zip_export_files(temp_dir_path, zip_file_name, zip_file_path, descriptor)
            zip_bytes = read_file(zip_file_path, "rb")

            self.set_header("Content-type", "application/zip")
            self.set_header("Content-Disposition", f"attachment; filename={zip_file_name}")
            self.write(zip_bytes)
            self.finish()

        except Exception as inst:
            render_error(self, traceback.format_exc())
        finally:
            content.remove_export_paths(zip_file_path, tmp_dir_path)

class ExportSubmissionsHandler(BaseUserHandler):
    def get(self, course):
        course_basics = content.get_course_basics(course)

        descriptor = f"Submissions_{course_basics['title'].replace(' ', '_')}"
        temp_dir_path, zip_file_name, zip_file_path = content.create_zip_file_path(descriptor)

        try:
            content.create_export_paths(temp_dir_path, descriptor)

            content.export_data(course_basics, "submissions", f"{temp_dir_path}/{descriptor}/submissions.json")

            content.zip_export_files(temp_dir_path, zip_file_name, zip_file_path, descriptor)
            zip_bytes = read_file(zip_file_path, "rb")

            self.set_header("Content-type", "application/zip")
            self.set_header("Content-Disposition", f"attachment; filename={zip_file_name}")
            self.write(zip_bytes)
            self.finish()

        except Exception as inst:
            render_error(self, traceback.format_exc())
        finally:
            content.remove_export_paths(zip_file_path, tmp_dir_path)

class AssignmentHandler(BaseUserHandler):
    def get(self, course, assignment):
        role = self.get_current_role()
        if role == "administrator" or role == "instructor" or role == "assistant":
            try:
                show = True
                assignment_basics = content.get_assignment_basics(course, assignment)
                assignment_id = assignment_basics["id"]
                out_file = f"Assignment_{assignment_id}_Scores.csv"
                self.render("assignment_admin.html", courses=content.get_courses(show), assignments=content.get_assignments(course, show), problems=content.get_problems(course, assignment, show), course_basics=content.get_course_basics(course), assignment_basics=assignment_basics, assignment_details=content.get_assignment_details(course, assignment, True), user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get(), role=role, out_file=out_file)
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            try:
                show = show_hidden(self.get_current_role())
                user_id = self.get_current_user()
                self.render("assignment.html", courses=content.get_courses(show), assignments=content.get_assignments(course, show), problems=content.get_problems(course, assignment, show), problem_statuses=content.get_problem_statuses(course, assignment, user_id), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), assignment_details=content.get_assignment_details(course, assignment, True), user_id=user_id, user_logged_in=user_logged_in_var.get())
            except Exception as inst:
                render_error(self, traceback.format_exc())

class EditAssignmentHandler(BaseUserHandler):
    def get(self, course, assignment):
        try:
            role = self.get_current_role()
            if role == "administrator" or role == "instructor" or role == "assistant":
                self.render("edit_assignment.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=content.get_problems(course, assignment), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), assignment_details=content.get_assignment_details(course, assignment), result=None, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            else:
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course, assignment):
        try:
            role = self.get_current_role()
            if role != "administrator" and role != "instructor" and role != "assistant":
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
                return

            title = self.get_body_argument("title").strip()
            visible = self.get_body_argument("is_visible") == "Yes"
            introduction = self.get_body_argument("introduction").strip()
            start_date = self.get_body_argument("start_date").strip()
            due_date = self.get_body_argument("due_date").strip()

            assignment_basics = content.get_assignment_basics(course, assignment)
            assignment_details = content.get_assignment_details(course, assignment)
            result = "Success: Assignment information saved!"

            if title == "" or introduction == "":
                result = "Error: Missing title or introduction."
            else:
                if content.has_duplicate_title(content.get_assignments(course), assignment_basics["id"], title):
                    result = "Error: An assignment with that title already exists."
                else:
                    if len(title) > 50:
                        result = "Error: The title cannot exceed 50 characters."
                    else:
                        content.specify_assignment_basics(assignment_basics, title, visible)
                        content.specify_assignment_details(assignment_details, introduction, None, datetime.datetime.now(), start_date, due_date)
                        assignment = content.save_assignment(assignment_basics, assignment_details)

            self.render("edit_assignment.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=content.get_problems(course, assignment), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), assignment_details=assignment_details, result=result, user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DeleteAssignmentHandler(BaseUserHandler):
    def get(self, course, assignment):
        try:
            role = self.get_current_role()
            if role == "administrator" or role == "instructor":
                self.render("delete_assignment.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=content.get_problems(course, assignment), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), result=None, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            else:
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course, assignment):
        try:
            role = self.get_current_role()
            if role != "administrator" and role != "instructor":
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
                return

            content.delete_assignment(content.get_assignment_basics(course, assignment))
            result = "Success: Assignment deleted."

            self.render("delete_assignment.html", courses=content.get_courses(), assignments=content.get_assignments(course), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), result=result, user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DeleteAssignmentSubmissionsHandler(BaseUserHandler):
    def get(self, course, assignment):
        try:
            role = self.get_current_role()
            if role == "administrator" or role == "instructor":
                self.render("delete_assignment_submissions.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=content.get_problems(course, assignment), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), result=None, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            else:
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course, assignment):
        try:
            role = self.get_current_role()
            if role != "administrator" and role != "instructor":
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
                return

            content.delete_assignment_submissions(content.get_assignment_basics(course, assignment))
            result = "Success: Assignment submissions deleted."

            self.render("delete_assignment_submissions.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=content.get_problems(course, assignment), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), result=result, user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ProblemHandler(BaseUserHandler):
    def get(self, course, assignment, problem):
        try:
            user = self.get_current_user()
            show = show_hidden(self.get_current_role())
            problems = content.get_problems(course, assignment, show)
            problem_details = content.get_problem_details(course, assignment, problem, format_content=True)
            back_end = settings_dict["back_ends"][problem_details["back_end"]]
            next_prev_problems = content.get_next_prev_problems(course, assignment, problem, problems)
            self.render("problem.html", courses=content.get_courses(show), assignments=content.get_assignments(course, show), problems=problems, course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), problem_basics=content.get_problem_basics(course, assignment, problem), problem_details=problem_details, next_problem=next_prev_problems["next"], prev_problem=next_prev_problems["previous"], code_completion_path=back_end["code_completion_path"], back_end_description=back_end["description"], num_submissions=content.get_num_submissions(course, assignment, problem, user), user_id=self.get_current_user(), student_id=self.get_current_user(), user_logged_in=user_logged_in_var.get(), role=self.get_current_role())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class EditProblemHandler(BaseUserHandler):
    def get(self, course, assignment, problem):
        try:
            role = self.get_current_role()
            if role == "administrator" or role == "instructor" or role == "assistant":
                problems = content.get_problems(course, assignment)
                problem_details = content.get_problem_details(course, assignment, problem)

                self.render("edit_problem.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=problems, course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), problem_basics=content.get_problem_basics(course, assignment, problem), problem_details=problem_details, next_prev_problems=content.get_next_prev_problems(course, assignment, problem, problems), code_completion_path=settings_dict["back_ends"][problem_details["back_end"]]["code_completion_path"], back_ends=sort_nicely(settings_dict["back_ends"].keys()), result=None, user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get(), role=role)
            else:
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course, assignment, problem):
        try:
            role = self.get_current_role()
            if role != "administrator" and role != "instructor":
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
                return

            problem_basics = content.get_problem_basics(course, assignment, problem)
            problem_details = content.get_problem_details(course, assignment, problem)

            problem_basics["title"] = self.get_body_argument("title").strip() #required
            problem_basics["visible"] = self.get_body_argument("is_visible") == "Yes"
            problem_details["instructions"] = self.get_body_argument("instructions").strip().replace("\r", "") #required
            problem_details["back_end"] = self.get_body_argument("back_end")
            problem_details["output_type"] = self.get_body_argument("output_type")
            problem_details["answer_code"] = self.get_body_argument("answer_code_text").strip().replace("\r", "") #required
            problem_details["answer_description"] = self.get_body_argument("answer_description").strip().replace("\r", "")
            problem_details["max_submissions"] = int(self.get_body_argument("max_submissions"))
            problem_details["test_code"] = self.get_body_argument("test_code_text").strip().replace("\r", "")
            problem_details["credit"] = self.get_body_argument("credit").strip().replace("\r", "")
            problem_details["data_url"] = self.get_body_argument("data_url").strip().replace("\r", "")
            problem_details["data_file_name"] = self.get_body_argument("data_file_name").strip().replace("\r", "")
            problem_details["show_expected"] = self.get_body_argument("show_expected") == "Yes"
            problem_details["show_test_code"] = self.get_body_argument("show_test_code") == "Yes"
            problem_details["show_answer"] = self.get_body_argument("show_answer") == "Yes"

            result = "Success: The problem was saved!"
            error_occurred = False

            if problem_basics["title"] == "" or problem_details["instructions"] == "" or problem_details["answer_code"] == "":
                result = "Error: One of the required fields is missing."
            else:
                if content.has_duplicate_title(content.get_problems(course, assignment), problem_basics["id"], problem_basics["title"]):
                    result = "Error: A problem with that title already exists in this assignment."
                else:
                    if len(problem_basics["title"]) > 50:
                        result = "Error: The title cannot exceed 50 characters."
                    else:
                        if (problem_details["data_url"] == "" and problem_details["data_file_name"] != "") or (problem_details["data_url"] != "" and problem_details["data_file_name"] == ""):
                            result = "Error: If a data URL or file name is specified, both must be specified."
                        else:
                            if problem_details["data_url"] == "":
                                data_contents = b""
                            else:
                                if not problem_details["data_file_name"] in problem_details["instructions"]:
                                    data_file_name = problem_details["data_file_name"]
                                    result = f"Error: You must mention {data_file_name} at least once in the instructions."
                                else:
                                    data_contents = download_file(problem_details["data_url"])

                                    # Make sure the file is not larger than 10 MB.
                                    if len(data_contents) > 10 * 1024 * 1024:
                                        data_url = problem_details["data_url"]
                                        result = f"Error: The file at {data_url} is too large ({len(data_contents)} bytes)."

                            if not result.startswith("Error:"):
                                content.specify_problem_basics(problem_basics, problem_basics["title"], problem_basics["visible"])
                                content.specify_problem_details(problem_details, problem_details["instructions"], problem_details["back_end"], problem_details["output_type"], problem_details["answer_code"],
                                problem_details["answer_description"], problem_details["max_submissions"], problem_details["test_code"], problem_details["credit"], problem_details["data_url"], problem_details["data_file_name"],
                                data_contents.decode(), problem_details["show_expected"], problem_details["show_test_code"], problem_details["show_answer"], "", None, datetime.datetime.now())

                                expected_output, error_occurred = exec_code(settings_dict["back_ends"][problem_details["back_end"]], problem_details["answer_code"], problem_basics, problem_details)

                                if problem_details["output_type"] == "txt" or error_occurred:
                                    expected_output = format_output_as_html(expected_output)
                                if error_occurred:
                                    result = "Code Error: " + expected_output
                                else:
                                    problem_details["expected_output"] = expected_output
                                    problem = content.save_problem(problem_basics, problem_details)
                                    problem_basics = content.get_problem_basics(course, assignment, problem)
                                    problem_details = content.get_problem_details(course, assignment, problem)

            problems = content.get_problems(course, assignment)
            self.render("edit_problem.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=problems, course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), problem_basics=problem_basics, problem_details=problem_details, next_prev_problems=content.get_next_prev_problems(course, assignment, problem, problems), code_completion_path=settings_dict["back_ends"][problem_details["back_end"]]["code_completion_path"], back_ends=sort_nicely(settings_dict["back_ends"].keys()), result=result, error_occurred=error_occurred, user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get(), role = self.get_current_role())
        except ConnectionError as inst:
            render_error(self, "The front-end server was unable to contact the back-end server to check your code.")
        except ReadTimeout as inst:
            render_error(self, f"Your code timed out after {settings_dict['back_ends'][problem_details['back_end']]['timeout_seconds']} seconds.")
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DeleteProblemHandler(BaseUserHandler):
    def get(self, course, assignment, problem):
        try:
            role = self.get_current_role()
            if role == "administrator" or role == "instructor":
                problems = content.get_problems(course, assignment)
                self.render("delete_problem.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=problems, course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), problem_basics=content.get_problem_basics(course, assignment, problem), next_prev_problems=content.get_next_prev_problems(course, assignment, problem, problems), result=None, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            else:
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course, assignment, problem):
        try:
            role = self.get_current_role()
            if role != "administrator" and role != "instructor":
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
                return

            content.delete_problem(content.get_problem_basics(course, assignment, problem))
            result = "Success: Problem deleted."

            problems = content.get_problems(course, assignment)
            self.render("delete_problem.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=problems, course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), problem_basics=content.get_problem_basics(course, assignment, problem), next_prev_problems=content.get_next_prev_problems(course, assignment, problem, problems), result=result, user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DeleteProblemSubmissionsHandler(BaseUserHandler):
    def get(self, course, assignment, problem):
        try:
            role = self.get_current_role()
            if role == "administrator" or role == "instructor":
                problems =content.get_problems(course, assignment)
                self.render("delete_problem_submissions.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=problems, course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), problem_basics=content.get_problem_basics(course, assignment, problem), next_prev_problems=content.get_next_prev_problems(course, assignment, problem, problems), result=None, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            else:
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course, assignment, problem):
        try:
            role = self.get_current_role()
            if role != "administrator" and role != "instructor":
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
                return

            content.delete_problem_submissions(content.get_problem_basics(course, assignment, problem))
            result = "Success: Problem submissions deleted."

            problems =content.get_problems(course, assignment)
            self.render("delete_problem_submissions.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=problems, course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), problem_basics=content.get_problem_basics(course, assignment, problem), next_prev_problems=content.get_next_prev_problems(course, assignment, problem, problems), result=result, user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class RunCodeHandler(BaseUserHandler):
    async def post(self, course, assignment, problem):
        user = self.get_current_user()
        code = self.get_body_argument("user_code").replace("\r", "")

        problem_basics = content.get_problem_basics(course, assignment, problem)
        problem_details = content.get_problem_details(course, assignment, problem)

        out_dict = {"error_occurred": True}

        try:
            code_output, error_occurred = exec_code(settings_dict["back_ends"][problem_details["back_end"]], code, problem_basics, problem_details, request=None)

            if problem_details["output_type"] == "txt" or error_occurred:
                code_output = format_output_as_html(code_output)

            out_dict["code_output"] = code_output
            out_dict["error_occurred"] = error_occurred
        except ConnectionError as inst:
            out_dict["code_output"] = "The front-end server was unable to contact the back-end server to check your code."
        except ReadTimeout as inst:
            out_dict["code_output"] = f"Your code timed out after {settings_dict['back_ends'][problem_details['back_end']]['timeout_seconds']} seconds."
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
        except ReadTimeout as inst:
            out_dict["code_output"] = f"Your code timed out after {settings_dict['back_ends'][problem_details['back_end']]['timeout_seconds']} seconds."
        except Exception as inst:
            out_dict["code_output"] = format_output_as_html(traceback.format_exc())

        self.write(json.dumps(out_dict))

class GetSubmissionHandler(BaseUserHandler):
    def get(self, course, assignment, problem, student_id, submission_id):
        try:
            problem_details = content.get_problem_details(course, assignment, problem)

            submission_info = content.get_submission_info(course, assignment, problem, student_id, submission_id)

            if submission_info["error_occurred"]:
                submission_info["diff_output"] = ""
            elif problem_details["output_type"] == "txt":
                submission_info["diff_output"] =  find_differences_txt(problem_details, submission_info["code_output"], submission_info["passed"])
            else:
                diff_image, diff_percent = diff_jpg(problem_details["expected_output"], submission_info["code_output"])
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

class ViewAnswerHandler(BaseUserHandler):
    def get(self, course, assignment, problem):
        try:
            user = self.get_current_user()
            self.render("view_answer.html", courses=content.get_courses(), assignments=content.get_assignments(course), problems=content.get_problems(course, assignment), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), problem_basics=content.get_problem_basics(course, assignment, problem), problem_details=content.get_problem_details(course, assignment, problem, format_content=True), last_submission=content.get_last_submission(course, assignment, problem, user), format_content=True, user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class AddAdminHandler(BaseUserHandler):
    def get(self):
        try:
            if self.get_current_role() == "administrator":
                self.render("add_admin.html", courses=content.get_courses(True), admins=content.get_users_from_role(0, "administrator"), result=None, user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get())
            else:
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self):
        try:
            if self.get_current_role() != "administrator":
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
                return

            new_admin = self.get_body_argument("new_admin")

            if content.check_user_exists(new_admin):
                if content.get_role(new_admin) == "administrator":
                    result = f"{new_admin} is already an administrator."
                else:
                    content.add_admin_permissions(new_admin)
                    result = f"Success! {new_admin} is an administrator."
            else:
                result = f"Error: The user '{new_admin}' does not exist."

            self.render("add_admin.html", courses=content.get_courses(), admins=content.get_users_from_role(0, "administrator"), result=result, user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class AddInstructorHandler(BaseUserHandler):
    def get(self, course):
        try:
            if self.get_current_role() == "administrator":
                course_basics = content.get_course_basics(course)
                self.render("add_instructor.html", courses=content.get_courses(), course_basics=course_basics, instructors=content.get_users_from_role(course_basics["id"], "instructor"), result=None, user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get())
            else:
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course):
        try:
            if self.get_current_role() != "administrator":
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
                return

            course_basics = content.get_course_basics(course)
            new_instructor = self.get_body_argument("new_inst")

            if content.check_user_exists(new_instructor):
                if content.get_role(new_instructor) == "administrator":
                    result = f"Error: {new_instructor} is already an administrator and can't be given a lower role."
                else:
                    content.add_permissions(course_basics["id"], new_instructor, "instructor")
                    result = f"Success! {new_instructor} is now an instructor for the {course_basics['title']} course."
            else:
                result = f"Error: The user '{new_instructor}' does not exist."

            self.render("add_instructor.html", courses=content.get_courses(), course_basics=course_basics, instructors=content.get_users_from_role(course_basics["id"], "instructor"), result=result, user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class AddAssistantHandler(BaseUserHandler):
    def get(self, course):
        try:
            role = self.get_current_role()
            if role == "administrator" or role == "instructor":
                course_basics = content.get_course_basics(course)
                self.render("add_assistant.html", courses=content.get_courses(), course_basics=course_basics, assistants=content.get_users_from_role(course_basics["id"], "assistant"), result=None, user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get())
            else:
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course):
        try:
            role = self.get_current_role()
            if role != "administrator" and role != "instructor":
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
                return

            course_basics = content.get_course_basics(course)
            new_assistant = self.get_body_argument("new_assistant")

            if content.check_user_exists(new_assistant):
                if content.get_role(new_assistant) == "administrator":
                    result = f"Error: {new_assistant} is already an administrator and can't be given a lower role."
                elif content.get_role(new_assistant) == "instructor":
                    result = f"Error: {new_assistant} is already an instructor and can't be given a lower role."
                else:
                    content.add_permissions(course_basics["id"], new_assistant, "assistant")
                    result = f"Success! {new_assistant} is an instructor's assistant for the {course_basics['title']} course."
            else:
                result = f"Error: The user '{new_assistant}' does not exist."

            self.render("add_assistant.html", courses=content.get_courses(), course_basics=course_basics, assistants=content.get_users_from_role(course_basics["id"], "assistant"), result=result, user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class RemoveAdminHandler(BaseUserHandler):
    def get(self, old_admin):
        try:
            role = self.get_current_role()
            if role == "administrator":
                self.render("remove_admin.html", courses=content.get_courses(), result=None, old_admin = old_admin, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            else:
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, old_admin):
        try:
            user_id=self.get_current_user()
            role = self.get_current_role()
            if role != "administrator":
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
                return

            if content.get_role(old_admin) != "administrator":
                result = f"Error: {old_admin} is not an administrator."
            else:
                if user_id != old_admin:
                    result = "Error: administrators can only be removed by themselves."
                else:
                    content.remove_permissions(None, old_admin, "administrator")
                    result = f"Success: {old_admin} has been removed from the administrator list."

            self.render("remove_admin.html", courses=content.get_courses(), result=result, user_id=user_id, user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class RemoveInstructorHandler(BaseUserHandler):
    def get(self, course, old_instructor):
        try:
            role = self.get_current_role()
            if role == "administrator":
                self.render("remove_instructor.html", courses=content.get_courses(), course_basics=content.get_course_basics(course), result=None, old_instructor = old_instructor, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            else:
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course, old_instructor):
        try:
            user_id=self.get_current_user()
            role = self.get_current_role()
            if role != "administrator":
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
                return

            if content.get_role(old_instructor) != "instructor":
                result = f"Error: {old_instructor} is not an instructor."
            else:
                content.remove_permissions(course, old_instructor, "instructor")
                result = f"Success: {old_instructor} has been removed from the instructor list."

            self.render("remove_instructor.html", courses=content.get_courses(), course_basics=content.get_course_basics(course), result=result, user_id=user_id, user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class RemoveAssistantHandler(BaseUserHandler):
    def get(self, course, old_assistant):
        try:
            role = self.get_current_role()
            if role == "administrator" or role == "instructor":
                self.render("remove_assistant.html", courses=content.get_courses(), course_basics=content.get_course_basics(course), result=None, old_assistant = old_assistant, user_id=user_id_var.get(), user_logged_in=user_logged_in_var.get())
            else:
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course, old_assistant):
        try:
            user_id=self.get_current_user()
            role = self.get_current_role()
            if role != "administrator" and role != "instructor":
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
                return

            if content.get_role(old_assistant) != "assistant":
                result = f"Error: {old_assistant} is not an assistant."
            else:
                content.remove_permissions(course, old_assistant, "assistant")
                result = f"Success: {old_assistant} has been removed from the instructor assistant list."

            self.render("remove_assistant.html", courses=content.get_courses(), course_basics=content.get_course_basics(course), result=result, user_id=user_id, user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DeleteUserHandler(BaseUserHandler):
    def get(self):
        try:
            role = self.get_current_role()
            if role == "administrator" or role == "instructor":
                self.render("delete_user.html", courses=content.get_courses(True), result=None, user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get())
            else:
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self):
        try:
            user_id=self.get_current_user()
            user = self.get_body_argument("delete_user")

            if content.check_user_exists(user):
                if content.get_role(user) == "administrator":
                    if len(content.get_users_from_role(0, "administrator")) > 1:
                        if user == user_id:
                            #Figure out what to do when admins remove themselves
                            content.delete_user(user)
                        else:
                            result = f"{user} is an administrator and can only be deleted by that user."
                    else:
                        result = f"Error: At least one administrator must remain in the system."
                elif content.get_role(user) == "instructor":
                    course_id = content.get_course_id_from_role(user)
                    if len(content.get_users_from_role(course_id, "instructor")) > 1:
                        if content.get_role(user_id) == "administrator":
                            content.delete_user(user)
                            result = f"Success: The user '{user}' has been deleted."
                        else:
                            result = "Instructors can only be removed by administrators."
                    else:
                        result = f"Error: The user '{user}' is the only instructor for their course. They cannot be deleted until another instructor is assigned to the course."
                else:
                    content.delete_user(user)
                    result = f"Success: The user '{user}' has been deleted."
            else:
                result = f"Error: The user '{user}' does not exist."

            self.render("delete_user.html", courses=content.get_courses(), result=result, user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())


class ViewScoresHandler(BaseUserHandler):
    def get(self, course, assignment):
        try:
            role = self.get_current_role()
            if role == "administrator" or role == "instructor" or role == "assistant":
                assignment_basics = content.get_assignment_basics(course, assignment)
                assignment_id = assignment_basics["id"]
                out_file = f"Assignment_{assignment_id}_Scores.csv"

                self.render("view_scores.html", courses=content.get_courses(), course_basics=content.get_course_basics(course), assignments=content.get_assignments(course), assignment_basics=assignment_basics, problems=content.get_problems(course, assignment), scores=content.get_assignment_scores(course, assignment), out_file=out_file, user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get())
            else:
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DownloadScoresHandler(BaseUserHandler):
    def get(self, course, assignment):
        try:
            role = self.get_current_role()
            if role == "administrator" or role == "instructor" or role == "assistant":
                csv_text = content.create_scores_text(course, assignment)
                self.set_header('Content-type', "text/csv")
                self.write(csv_text)
            else:
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            self.write(traceback.format_exc())
            #render_error(self, traceback.format_exc())

class StudentScoresHandler(BaseUserHandler):
    def get(self, course, assignment, student_id):
        try:
            role = self.get_current_role()
            if role == "administrator" or role == "instructor" or role == "assistant":
                self.render("student_scores.html", student_id=student_id, courses=content.get_courses(), course_basics=content.get_course_basics(course), assignments=content.get_assignments(course), assignment_basics=content.get_assignment_basics(course, assignment), problems=content.get_problems(course, assignment), problem_statuses=content.get_problem_statuses(course, assignment, student_id), user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get())
            else:
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class StudentProblemHandler(BaseUserHandler):
    def get(self, course, assignment, problem, student_id):
        try:
            role = self.get_current_role()
            if role == "administrator" or role == "instructor" or role == "assistant":
                show = True
                problems = content.get_problems(course, assignment, show)
                problem_details = content.get_problem_details(course, assignment, problem, format_content=True)
                back_end = settings_dict["back_ends"][problem_details["back_end"]]
                next_prev_problems=content.get_next_prev_problems(course, assignment, problem, problems)

                self.render("student_problem.html", student_id=student_id, courses=content.get_courses(show), course_basics=content.get_course_basics(course), assignments=content.get_assignments(course, show), assignment_basics=content.get_assignment_basics(course, assignment), problems=problems, problem_basics=content.get_problem_basics(course, assignment, problem), problem_details=problem_details, next_problem=next_prev_problems["next"], code_completion_path=back_end["code_completion_path"], back_end_description=back_end["description"], num_submissions=content.get_num_submissions(course, assignment, problem, student_id), user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get(), role=role)
            else:
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class BackEndHandler(RequestHandler):
    def get(self, back_end):
        try:
            self.write(json.dumps(settings_dict["back_ends"][back_end]))
        except Exception as inst:
            logging.error(self, traceback.format_exc())
            self.write(json.dumps({"Error": "An error occurred."}))

class SummarizeLogsHandler(BaseUserHandler):
    def get(self):
        try:
            if self.get_current_role() == "administrator":
                years, months, days = get_list_of_dates()
                self.render("summarize_logs.html", filter_list = sorted(content.get_root_dirs_to_log()), years=years, months=months, days=days, show_table=False, user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get())
            else:
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self):
        try:
            if self.get_current_role() != "administrator":
                self.render("permissions.html", user_logged_in=user_logged_in_var.get())
                return

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

            self.render("summarize_logs.html", filter = filter, filter_list = sorted(content.get_root_dirs_to_log()), years=years, months=months, days=days, log_dict=content.get_log_table_contents(log_file, year, month, day), show_table=True, user_id=self.get_current_user(), user_logged_in=user_logged_in_var.get())
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

class DevelopmentLoginHandler(RequestHandler):
    def get(self, target_path):
        if not target_path:
            target_path = ""

        self.render("devlogin.html", courses=content.get_courses(False), target_path=target_path)

    def post(self, target_path):
        try:
            user_id = self.get_body_argument("user_id")

            if user_id == "":
                self.write("Invalid user ID.")
            else:
                if not content.check_user_exists(user_id):
                    # Add static information for test user.
                    user_dict = {'id': user_id, 'email': 'test_user@gmail.com', 'verified_email': True, 'name': 'Test User', 'given_name': 'Test', 'family_name': 'User', 'picture': 'https://vignette.wikia.nocookie.net/simpsons/images/1/15/Capital_City_Goofball.png/revision/latest?cb=20170903212224', 'locale': 'en'}
                    content.add_user(user_id, user_dict)

                self.set_secure_cookie("user_id", user_id, expires_days=30)

                if not target_path:
                    target_path = "/"
                self.redirect(target_path)

                #content.update_tables_for_due_date()
        except Exception as inst:
            render_error(self, traceback.format_exc())

class GoogleLoginHandler(RequestHandler, GoogleOAuth2Mixin):
    async def get(self):
        try:
            redirect_uri = f"https://{settings_dict['domain']}/login"

            # Examples: https://www.programcreek.com/python/example/95028/tornado.auth
            if self.get_argument('code', False):
                user_dict = await self.get_authenticated_user(redirect_uri = redirect_uri, code = self.get_argument('code'))

                if user_dict:
                    response = urllib.request.urlopen(f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={user_dict['access_token']}").read()

                    if response:
                        user_dict = json.loads(response.decode('utf-8'))
                        user_id = user_dict["email"]

                        if content.check_user_exists(user_id):
                            # Update user with current information when they already exist.
                            content.update_user(user_id, user_dict)
                        else:
                            # Store current user information when they do not already exist.
                            content.add_user(user_id, user_dict)

                        self.set_secure_cookie("user_id", user_id, expires_days=30)

                        redirect_path = self.get_secure_cookie("redirect_path")
                        self.clear_cookie("redirect_path")
                        if not redirect_path:
                            redirect_path = "/"
                        self.redirect(redirect_path)
                    else:
                        self.clear_all_cookies()
                        render_error(self, "Google account information could not be retrieved.")
                else:
                    self.clear_all_cookies()
                    render_error(self, "Google authentication failed. Your account could not be authenticated.")
            else:
                await self.authorize_redirect(
                    redirect_uri = redirect_uri,
                    client_id = self.settings['google_oauth']['key'],
                    scope = ['profile', 'email'],
                    response_type = 'code',
                    extra_params = {'approval_prompt': 'auto'})
        except Exception as inst:
            render_error(self, traceback.format_exc())

class LogoutHandler(BaseUserHandler):
    def get(self):
        try:
            self.clear_all_cookies()

            if settings_dict["mode"] == "production":
                self.redirect("https://accounts.google.com/Logout")
            else:
                self.redirect("/")
        except Exception as inst:
            render_error(self, traceback.format_exc())

# See https://quanttype.net/posts/2020-02-05-request-id-logging.html
class LoggingFilter(logging.Filter):
    def filter(self, record):
        record.user_id = user_id_var.get("-")
        return True

if __name__ == "__main__":
    if "PORT" in os.environ and "MPORT" in os.environ:
        application = make_app()

        secrets_dict = load_yaml_dict(read_file("/app/secrets.yaml"))
        application.settings["cookie_secret"] = secrets_dict["cookie"]
        application.settings["google_oauth"] = {
            "key": secrets_dict["google_oauth_key"],
            "secret": secrets_dict["google_oauth_secret"]}
        settings_dict = load_yaml_dict(read_file("/Settings.yaml"))

        content = Content(settings_dict)
        content.create_sqlite_tables()

        server = tornado.httpserver.HTTPServer(application)
        server.bind(int(os.environ['PORT']))
        server.start(int(os.environ['NUM_PROCESSES']))

        user_id_var = contextvars.ContextVar("user_id")
        user_logged_in_var = contextvars.ContextVar("user_logged_in")
        user_role_var = contextvars.ContextVar("user_role")

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
