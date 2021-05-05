from content import *
import contextvars
from datetime import datetime
import glob
from helper import *
import html
import io
import json
import logging
import os
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
        url(r"\/profile\/courses\/([^\/]+)", ProfileCoursesHandler, name="profile_courses"),
        url(r"\/profile\/personal_info\/([^\/]+)", ProfilePersonalInfoHandler, name="profile_personal_info"),
        url(r"\/profile\/admin\/([^\/]+)", ProfileAdminHandler, name="profile_admin"),
        url(r"\/profile\/instructor\/course\/([^\/]+)", ProfileSelectCourseHandler, name="profile_select_course"),
        url(r"\/profile\/instructor\/([^\/]+)\/([^\/]+)", ProfileInstructorHandler, name="profile_instructor"),
        url(r"\/profile\/manage_users", ProfileManageUsersHandler, name="profile_manage_users"),
        url(r"\/profile\/help_requests", ProfileHelpRequestsHandler, name="profile_help_requests"),
        url(r"\/profile\/student_help_requests", ProfileStudentHelpRequestsHandler, name="profile_student_help_requests"),
        url(r"\/profile\/preferences\/([^\/]+)", ProfilePreferencesHandler, name="profile_preferences"),
        url(r"\/unregister\/([^\/]+)\/([^\/]+)", UnregisterHandler, name="unregister"),
        url(r"\/course\/([^\/]+)", CourseHandler, name="course"),
        url(r"\/edit_course\/([^\/]+)?", EditCourseHandler, name="edit_course"),
        url(r"\/delete_course\/([^\/]+)?", DeleteCourseHandler, name="delete_course"),
        url(r"\/delete_course_submissions\/([^\/]+)?", DeleteCourseSubmissionsHandler, name="delete_course_submissions"),
        url(r"\/import_course", ImportCourseHandler, name="import_course"),
        url(r"\/export_course\/([^\/]+)?", ExportCourseHandler, name="export_course"),
        url(r"\/export_submissions\/([^\/]+)?", ExportSubmissionsHandler, name="export_submissions"),
        url(r"\/assignment\/([^\/]+)\/([^\/]+)", AssignmentHandler, name="assignment"),
        url(r"\/edit_assignment\/([^\/]+)\/([^\/]+)?", EditAssignmentHandler, name="edit_assignment"),
        url(r"\/copy_assignment\/([^\/]+)\/([^\/]+)?", CopyAssignmentHandler, name="copy_assignment"),
        url(r"\/delete_assignment\/([^\/]+)\/([^\/]+)?", DeleteAssignmentHandler, name="delete_assignment"),
        url(r"\/delete_assignment_submissions\/([^\/]+)\/([^\/]+)?", DeleteAssignmentSubmissionsHandler, name="delete_assignment_submissions"),
        url(r"\/exercise\/([^\/]+)\/([^\/]+)/([^\/]+)", ExerciseHandler, name="exercise"),
        url(r"\/edit_exercise\/([^\/]+)\/([^\/]+)/([^\/]+)?", EditExerciseHandler, name="edit_exercise"),
        url(r"\/create_video_exercise\/([^\/]+)\/([^\/]+)", CreateVideoExerciseHandler, name="create_video_exercise"),
        url(r"\/move_exercise\/([^\/]+)\/([^\/]+)/([^\/]+)?", MoveExerciseHandler, name="move_exercise"),
        url(r"\/delete_exercise\/([^\/]+)\/([^\/]+)/([^\/]+)?", DeleteExerciseHandler, name="delete_exercise"),
        url(r"\/delete_exercise_submissions\/([^\/]+)\/([^\/]+)/([^\/]+)?", DeleteExerciseSubmissionsHandler, name="delete_exercise_submissions"),
        url(r"\/run_code\/([^\/]+)\/([^\/]+)/([^\/]+)", RunCodeHandler, name="run_code"),
        url(r"\/submit\/([^\/]+)\/([^\/]+)/([^\/]+)", SubmitHandler, name="submit"),
        url(r"\/get_submission\/([^\/]+)\/([^\/]+)/([^\/]+)/([^\/]+)/(\d+)", GetSubmissionHandler, name="get_submission"),
        url(r"\/get_submissions\/([^\/]+)\/([^\/]+)/([^\/]+)/([^\/]+)", GetSubmissionsHandler, name="get_submissions"),
        url(r"\/view_answer\/([^\/]+)\/([^\/]+)/([^\/]+)", ViewAnswerHandler, name="view_answer"),
        url(r"\/add_instructor\/([^\/]+)", AddInstructorHandler, name="add_instructor"),
        url(r"\/remove_admin\/([^\/]+)", RemoveAdminHandler, name="remove_admin"),
        url(r"\/remove_instructor\/([^\/]+)\/([^\/]+)", RemoveInstructorHandler, name="remove_instructor"),
        url(r"\/remove_assistant\/([^\/]+)\/([^\/]+)", RemoveAssistantHandler, name="remove_assistant"),
        url(r"\/reset_timer\/([^\/]+)\/([^\/]+)\/([^\/]+)", ResetTimerHandler, name="reset_timer"),
        url(r"\/view_scores\/([^\/]+)\/([^\/]+)", ViewScoresHandler, name="view_scores"),
        url(r"\/download_file\/([^\/]+)\/([^\/]+)/([^\/]+)/([^\/]+)", DownloadFileHandler, name="download_file"),
        url(r"\/download_scores\/([^\/]+)\/([^\/]+)", DownloadScoresHandler, name="download_scores"),
        url(r"\/download_all_scores\/([^\/]+)", DownloadAllScoresHandler, name="download_all_scores"),
        url(r"\/edit_scores\/([^\/]+)\/([^\/]+)\/([^\/]+)", EditScoresHandler, name="edit_scores"),
        url(r"\/student_scores\/([^\/]+)\/([^\/]+)\/([^\/]+)", StudentScoresHandler, name="student_scores"),
        url(r"\/student_exercise\/([^\/]+)\/([^\/]+)/([^\/]+)/([^\/]+)", StudentExerciseHandler, name="student_exercise"),
        url(r"\/exercise_scores\/([^\/]+)\/([^\/]+)\/([^\/]+)", ExerciseScoresHandler, name="exercise_scores"),
        url(r"\/exercise_submissions\/([^\/]+)\/([^\/]+)\/([^\/]+)", ExerciseSubmissionsHandler, name="exercise_submissions"),
        url(r"\/help_requests\/([^\/]+)", HelpRequestsHandler, name="help_requests"),
        url(r"\/submit_request\/([^\/]+)\/([^\/]+)\/([^\/]+)", SubmitHelpRequestHandler, name="submit_request"),
        url(r"\/view_request\/([^\/]+)\/([^\/]+)\/([^\/]+)\/([^\/]+)", ViewHelpRequestsHandler, name="view_request"),
        url(r"\/delete_request\/([^\/]+)\/([^\/]+)\/([^\/]+)\/([^\/]+)", DeleteHelpRequestHandler, name="delete_request"),
        url(r"\/back_end\/([^\/]+)", BackEndHandler, name="back_end"),
        url(r"/static/(.+)", StaticFileHandler, name="static_file"),
        url(r"\/summarize_logs", SummarizeLogsHandler, name="summarize_logs"),
        url(r"/login", GoogleLoginHandler, name="login"),
        url(r"/devlogin(/.+)?", DevelopmentLoginHandler, name="devlogin"),
        url(r"/logout", LogoutHandler, name="logout"),
    ], autoescape=None)

#        url(r"\/initialize", InitializeHandler, name="initialize"),
    return app

class HomeHandler(RequestHandler):
    def prepare(self):
        try:
            user_id = self.get_secure_cookie("user_id")

            # Set context variables depending on whether the user is logged in.
            if user_id:
                user_id = user_id.decode()
                user_info_var.set(user_id)
            else:
                user_info_var.set(self.request.remote_ip)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def get(self):
        try:
            user_id = self.get_secure_cookie("user_id")

            if content.get_user_count() > 0 and not content.administrator_exists():
                if user_id:
                    content.add_admin_permissions(user_id.decode())
                    user_is_administrator_var.set(True)
                    self.redirect(f"/profile/courses/{user_id.decode()}")
                else:
                    if settings_dict["mode"] == "production":
                        self.set_secure_cookie("redirect_path", "/")
                        self.redirect("/login")
                    else:
                        self.redirect("/devlogin")
            else:
                if user_id:
                    self.redirect(f"/profile/courses/{user_id.decode()}")
                else:
                    self.render("home.html", mode=settings_dict["mode"])
        except Exception as inst:
            render_error(self, traceback.format_exc())

class BaseUserHandler(RequestHandler):
    def prepare(self):
        try:
            user_id = self.get_secure_cookie("user_id")

            # Set context variables depending on whether the user is logged in.
            if user_id:
                user_info_var.set(content.get_user_info(user_id.decode()))
                user_is_administrator_var.set(content.is_administrator(user_id.decode()))
                user_instructor_courses_var.set([str(x) for x in content.get_courses_with_role(user_id.decode(), "instructor")])
                user_assistant_courses_var.set([str(x) for x in content.get_courses_with_role(user_id.decode(), "assistant")])
            else:
                if settings_dict["mode"] == "production":
                    self.set_secure_cookie("redirect_path", self.request.path)
                    self.redirect("/login")
                else:
                    self.redirect("/devlogin{}".format(self.request.path))
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def get_user_info(self):
        return user_info_var.get()

    def get_user_id(self):
        return self.get_user_info()["user_id"]

    def is_administrator(self):
        return user_is_administrator_var.get()

    def is_instructor(self):
        return len(user_instructor_courses_var.get()) > 0

    def is_assistant(self):
        return len(user_assistant_courses_var.get()) > 0

    def is_instructor_for_course(self, course_id):
        return course_id in user_instructor_courses_var.get()

    def is_assistant_for_course(self, course_id):
        return course_id in user_assistant_courses_var.get()

    def is_student_for_course(self, course_id):
        return not self.is_administrator() and not self.is_instructor_for_course(course_id) and not self.is_assistant_for_course(course_id)

class ProfileCoursesHandler(BaseUserHandler):
    def get(self, user_id):
        try:
            if self.is_administrator():
                registered_courses = content.get_courses()
                available_courses = None
            elif self.is_instructor() or self.is_assistant():
                registered_courses = content.get_courses_connected_to_user(user_id)
                available_courses = None
            else:
                registered_courses = content.get_registered_courses(user_id)
                available_courses = content.get_available_courses(user_id)

            self.render("profile_courses.html", page="courses", result=None, available_courses=available_courses, registered_courses=registered_courses, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, user_id):
        try:
            course_id = self.get_body_argument("course_id")
            passcode = self.get_body_argument("passcode")

            course_basics = content.get_course_basics(course_id)
            course_details = content.get_course_details(course_id)
            course_title = course_basics["title"]
            course_passcode = course_details["passcode"]
            result = ""

            if (course_passcode == None or course_passcode == passcode):
                if (content.course_exists(course_id)):
                    if (content.check_user_registered(course_id, user_id)):
                        result = f"Error: You are already registered for {course_title}."
                    else:
                        content.register_user_for_course(course_id, user_id)
                        result = f"Success: You're now registered for {course_title}."
                else:
                    result = "Error: A course with that ID was not found."
            elif passcode == "":
                result = "Error: Please enter a passcode."
            else:
                result = "Error: Incorrect passcode."

            if self.is_administrator():
                registered_courses = content.get_courses()
                available_courses = None
            elif self.is_instructor() or self.is_assistant():
                registered_courses = content.get_courses_connected_to_user(user_id)
                available_courses = None
            else:
                registered_courses = content.get_registered_courses(user_id)
                available_courses = content.get_available_courses(user_id)

            self.render("profile_courses.html", page="courses", result=result, available_courses=available_courses, registered_courses=registered_courses, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ProfilePersonalInfoHandler(BaseUserHandler):
    def get(self, user_id):
        try:
            self.render("profile_personal_info.html", page="personal_info", user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ProfileAdminHandler(BaseUserHandler):
    def get (self, user_id):
        try:
            if self.is_administrator():
                self.render("profile_admin.html", page="admin", tab=None, admins=content.get_users_from_role(0, "administrator"), result=None, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, user_id):
        try:
            if not self.is_administrator():
                self.render("permissions.html")
                return

            new_admin = self.get_body_argument("new_admin")

            if content.user_exists(new_admin):
                if content.is_administrator(new_admin):
                    result = f"{new_admin} is already an administrator."
                else:
                    content.add_admin_permissions(new_admin)
                    result = f"Success! {new_admin} is an administrator."
            else:
                result = f"Error: The user '{new_admin}' does not exist."

            self.render("profile_admin.html", page="admin", tab="manage", admins=content.get_users_from_role(0, "administrator"), result=result, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ProfileSelectCourseHandler(BaseUserHandler):
    def get(self, user_id):
        try:
            if self.is_administrator():
                courses = content.get_courses()
            elif self.is_instructor():
                courses = content.get_courses_connected_to_user(user_id)

            if len(courses) > 1:
                self.render("profile_select_course.html", courses=courses, page="instructor", user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
            else:
                self.render("profile_instructor.html", page="instructor", tab=None, course=courses[0][1], assignments=content.get_assignments(courses[0][0]), instructors=content.get_users_from_role(courses[0][0], "instructor"), assistants=content.get_users_from_role(courses[0][0], "assistant"), registered_students=content.get_registered_students(courses[0][0]), result=None, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(courses[0][0]), is_assistant=self.is_assistant_for_course(courses[0][0]))
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ProfileInstructorHandler(BaseUserHandler):
    def get (self, course_id, user_id):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course_id):
                self.render("profile_instructor.html", page="instructor", tab=None, course=content.get_course_basics(course_id), assignments=content.get_assignments(course_id), instructors=content.get_users_from_role(course_id, "instructor"), assistants=content.get_users_from_role(course_id, "assistant"), registered_students=content.get_registered_students(course_id), result=None, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course_id), is_assistant=self.is_assistant_for_course(course_id))
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course_id, user_id):
        try:
            new_assistant = self.get_body_argument("new_assistant")
            new_instructor = self.get_body_argument("new_instructor")
            result = ""
            tab = ""

            if new_assistant:
                tab = "manage_assistants"
                if self.is_administrator() or self.is_instructor_for_course(course_id):
                    if content.user_exists(new_assistant):
                        if content.user_has_role(new_assistant, course_id, "assistant"):
                            result = f"{new_assistant} is already an assistant for this course."
                        else:
                            content.add_permissions(course_id, new_assistant, "assistant")
                            result = f"Success! {new_assistant} is now an assistant for this course."
                    else:
                        result = f"Error: The user '{new_assistant}' does not exist."
                else:
                    self.render("permissions.html")

            elif new_instructor:
                tab = "manage_instructors"
                if self.is_administrator():
                    if content.user_exists(new_instructor):
                        if content.user_has_role(new_instructor, course_id, "instructor"):
                            result = f"{new_instructor} is already an instructor for this course."
                        else:
                            content.add_permissions(course_id, new_instructor, "instructor")
                            result = f"Success! {new_instructor} is now an instructor for this course."
                    else:
                        result = f"Error: The user '{new_instructor}' does not exist."
                else:
                    self.render("permissions.html")

            self.render("profile_instructor.html", page="instructor", tab=tab, course=content.get_course_basics(course_id), assignments=content.get_assignments(course_id), instructors=content.get_users_from_role(course_id, "instructor"), assistants=content.get_users_from_role(course_id, "assistant"), registered_students=content.get_registered_students(course_id), result=result, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course_id), is_assistant=self.is_assistant_for_course(course_id))
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ProfileManageUsersHandler(BaseUserHandler):
    def get(self):
        try:
            if self.is_administrator() or self.is_instructor():
                self.render("profile_manage_users.html", page="manage_users", result=None, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self):
        try:
            remove_user = self.get_body_argument("remove_user")
            delete_user = self.get_body_argument("delete_user")

            if remove_user:
                if content.user_exists(remove_user):
                    submissions_removed = content.remove_user_submissions(remove_user)
                    if submissions_removed:
                        result = f"Success: All scores and submissions for the user '{remove_user}' have been deleted."
                    else:
                        result = f"Error: The user '{remove_user}' doesn't have any submissions to remove."
                else:
                    result = f"Error: The user '{remove_user}' does not exist."

            if delete_user:
                course_id = content.get_course_id_from_role(delete_user)

                if content.user_exists(delete_user):
                    if content.is_administrator(delete_user):
                        if len(content.get_users_from_role(0, "administrator")) > 1:
                            if delete_user == self.get_user_id():
                                #Figure out what to do when admins remove themselves
                                content.delete_user(delete_user)
                            else:
                                result = f"{delete_user} is an administrator and can only be deleted by that user."
                        else:
                            result = f"Error: At least one administrator must remain in the system."
                    elif content.user_has_role(delete_user, course_id, "instructor"):
                        if len(content.get_users_from_role(course_id, "instructor")) > 1:
                            if content.is_administrator(user_id):
                                content.delete_user(delete_user)
                                result = f"Success: The user '{delete_user}' has been deleted."
                            else:
                                result = "Instructors can only be removed by administrators."
                        else:
                            result = f"Error: The user '{delete_user}' is the only instructor for their course. They cannot be deleted until another instructor is assigned to the course."
                    else:
                        content.delete_user(delete_user)
                        result = f"Success: The user '{delete_user}' has been deleted."
                else:
                    result = f"Error: The user '{delete_user}' does not exist."

            self.render("profile_manage_users.html", page="manage_users", result=result, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ProfileHelpRequestsHandler(BaseUserHandler):
    def get(self):
        try:
            if self.is_administrator() or self.is_instructor() or self.is_assistant():
                user_info=self.get_user_info()
                if self.is_administrator():
                    courses = content.get_courses()
                elif self.is_instructor() or self.is_assistant():
                    courses = content.get_courses_connected_to_user(user_info["user_id"])

                self.render("profile_help_requests.html", page="help_requests", result=None, courses=courses, user_info=user_info, is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ProfileStudentHelpRequestsHandler(BaseUserHandler):
    def get(self):
        try:
            self.render("profile_student_help_requests.html", page="help_requests", result=None, user_info=self.get_user_info(), help_requests=content.get_student_help_requests(self.get_user_id()), is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ProfilePreferencesHandler(BaseUserHandler):
    def get(self, user_id):
        try:
            ace_themes = ["ambiance", "chaos", "chrome", "clouds", "cobalt", "dracula", "github", "kr_theme", "monokai", "sqlserver", "terminal", "tomorrow", "xcode"]
            self.render("profile_preferences.html", page="preferences", code_completion_path="ace/mode/r", ace_themes=ace_themes, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, user_id):
        try:
            ace_theme = self.get_body_argument("ace_theme")
            use_auto_complete = self.get_body_argument("use_auto_complete") == "Yes"
            content.update_user_settings(user_id, ace_theme, use_auto_complete)
            ace_themes = ["ambiance", "chaos", "chrome", "clouds", "cobalt", "dracula", "github", "kr_theme", "monokai", "sqlserver", "terminal", "tomorrow", "xcode"]
            self.render("profile_preferences.html", page="preferences", code_completion_path="ace/mode/r", ace_themes=ace_themes, user_info=content.get_user_info(user_id), is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class UnregisterHandler(BaseUserHandler):
    def post(self, course, user_id):
        try:
            if (self.is_student_for_course(course) and self.get_user_id() == user_id) or self.is_administrator() or self.is_instructor_for_course(course):
                if content.check_user_registered(course, user_id):
                    content.unregister_user_from_course(course, user_id)
                    title = content.get_course_basics(course)["title"]
                    result = f"Success: The user {user_id} has been removed from {title}"
                else:
                    result = f"Error: The user {user_id} is not currently registered for the course \"{title}\""

                if self.is_administrator() or self.is_instructor_for_course(course):
                    self.render("profile_instructor.html", page="instructor", tab="manage_students", course=content.get_course_basics(course), assignments=content.get_assignments(course), instructors=content.get_users_from_role(course, "instructor"), assistants=content.get_users_from_role(course, "assistant"), registered_students=content.get_registered_students(course), result=result, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course))
            else:
                self.render("permissions.html", user_info=content.get_user_info(self.get_user_id()), user_logged_in=user_logged_in_var.get())

        except Exception as inst:
            render_error(self, traceback.format_exc())

class CourseHandler(BaseUserHandler):
    def get(self, course):
        if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
            try:
                assignments = content.get_assignments(course, True)

                self.render("course_admin.html", courses=content.get_courses(True), assignments=assignments, course_basics=content.get_course_basics(course), course_details=content.get_course_details(course, True), course_scores=content.get_course_scores(course, assignments), user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course))
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            try:
                self.render("course.html", courses=content.get_courses(False), assignments=content.get_assignments(course, False), assignment_statuses=content.get_assignment_statuses(course, self.get_user_id()), course_basics=content.get_course_basics(course), course_details=content.get_course_details(course, True), curr_datetime=datetime.datetime.now(), user_info=self.get_user_info())
            except Exception as inst:
                render_error(self, traceback.format_exc())

class EditCourseHandler(BaseUserHandler):
    def get(self, course):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course):
                self.render("edit_course.html", courses=content.get_courses(), assignments=content.get_assignments(course), course_basics=content.get_course_basics(course), course_details=content.get_course_details(course), result=None, user_info=self.get_user_info())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course):
        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                self.render("permissions.html")
                return

            course_basics = content.get_course_basics(course)
            course_details = content.get_course_details(course)

            course_basics["title"] = self.get_body_argument("title").strip()
            course_basics["visible"] = self.get_body_argument("is_visible") == "Yes"
            course_details["introduction"] = self.get_body_argument("introduction").strip()
            course_details["passcode"] = self.get_body_argument("passcode").strip()

            if course_details["passcode"] == "":
                course_details["passcode"] = None

            result = "Success: Course information saved!"

            if course_basics["title"] == "" or course_details["introduction"] == "":
                result = "Error: Missing title or introduction."
            else:
                if content.has_duplicate_title(content.get_courses(), course_basics["id"], course_basics["title"]):
                    result = "Error: A course with that title already exists."
                else:
                    #if re.search(r"[^\w ]", title):
                    #    result = "Error: The title can only contain alphanumeric characters and spaces."
                    #else:
                    if len(course_basics["title"]) > 30:
                        result = "Error: The title cannot exceed 30 characters."
                    else:
                        #content.specify_course_basics(course_basics, course_basics["title"], course_basics["visible"])
                        content.specify_course_details(course_details, course_details["introduction"], course_details["passcode"], None, datetime.datetime.now())
                        course = content.save_course(course_basics, course_details)

            self.render("edit_course.html", courses=content.get_courses(), assignments=content.get_assignments(course), course_basics=course_basics, course_details=course_details, result=result, user_info=self.get_user_info())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DeleteCourseHandler(BaseUserHandler):
    def get(self, course):
        try:
            if self.is_administrator():
                self.render("delete_course.html", courses=content.get_courses(), course_basics=content.get_course_basics(course), result=None, user_info=self.get_user_info())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course):
        try:
            if not self.is_administrator():
                self.render("permissions.html")
                return

            content.delete_course(content.get_course_basics(course))
            result = "Success: Course deleted."

            self.render("delete_course.html", courses=content.get_courses(), course_basics=content.get_course_basics(None), result=result, user_info=self.get_user_info())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DeleteCourseSubmissionsHandler(BaseUserHandler):
    def post(self, course):
        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                self.render("permissions.html")
                return

            content.delete_course_submissions(content.get_course_basics(course))
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ImportCourseHandler(BaseUserHandler):
    def post(self):
        try:
            if not self.is_administrator():
                self.render("permissions.html")
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

                    exercise_lists = json.loads(zip_file.read(f"{descriptor}/exercises.json"))
                    for exercise_list in exercise_lists:
                        exercise_id = None
                        exercise_basics = content.get_exercise_basics(course_basics["id"], assignment_id_dict[exercise_list[1]], exercise_id)
                        exercise_details = content.get_exercise_details(course_basics["id"], assignment_id_dict[exercise_list[1]], exercise_id)

                        content.specify_exercise_basics(exercise_basics, exercise_list[3], bool(exercise_list[4]))

                        answer_code = exercise_list[5]
                        answer_description = exercise_list[6]
                        hint = ""
                        max_submissions = int(exercise_list[7])
                        credit = exercise_list[8]
                        data_files = exercise_list[9]
                        back_end = exercise_list[10]
                        instructions = exercise_list[12]
                        output_type = exercise_list[13]
                        show_answer = bool(exercise_list[14])
                        show_student_submissions = bool(exercise_list[15])
                        show_expected = bool(exercise_list[16])
                        show_test_code = bool(exercise_list[17])
                        starter_code = exercise_list[18]
                        test_code = exercise_list[19]
                        date_created = convert_string_to_date(exercise_list[20])
                        date_updated = convert_string_to_date(exercise_list[21])

                        expected_text_output = ""
                        expected_image_output = ""
                        if expected_output == "txt":
                            expected_text_output = exercise_list[13]
                        else:
                            expected_image_output = exercise_list[13]

                        content.specify_exercise_details(exercise_details, instructions, back_end, output_type, answer_code, answer_description, hint, max_submissions, starter_code, test_code, credit, data_files, show_expected, show_test_code, show_answer, expected_output, date_created, date_updated)
                        content.save_exercise(exercise_basics, exercise_details)

                    result = "Success: The course was imported!"
            else:
                result = "Error: The uploaded file was not recognized as a zip file."

            self.render("profile_admin.html", page="admin", tab="import", admins=content.get_users_from_role(0, "administrator"), result=result, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ExportCourseHandler(BaseUserHandler):
    def get(self, course):
        course_basics = content.get_course_basics(course)

        descriptor = f"Course_{course_basics['title'].replace(' ', '_')}"
        temp_dir_path, zip_file_name, zip_file_path = content.create_zip_file_path(descriptor)

        try:
            content.create_export_paths(temp_dir_path, descriptor)

            for table_name in ["courses", "assignments", "exercises"]:
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
        if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
            try:
                assignment_basics = content.get_assignment_basics(course, assignment)

                self.render("assignment_admin.html", courses=content.get_courses(True), assignments=content.get_assignments(course, True), exercises=content.get_exercises(course, assignment, True), exercise_statuses=content.get_exercise_statuses(course, assignment, self.get_user_info()["user_id"]), course_basics=content.get_course_basics(course), assignment_basics=assignment_basics, assignment_details=content.get_assignment_details(course, assignment, True), course_options=[x[1] for x in content.get_courses() if str(x[0]) != course], user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course), download_file_name=get_scores_download_file_name(assignment_basics))
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            try:
                user_info = self.get_user_info()
                assignment_details = content.get_assignment_details(course, assignment, True)
                curr_datetime = datetime.datetime.now()
                start_time = content.get_user_assignment_start_time(course, assignment, user_info["user_id"])

                # Zach was here
                if client_ip not in assignment_details["valid_ip_addresses"]:
                    self.render("unavailable_assignment.html", courses=content.get_courses(),
                                assignments=content.get_assignments(course),
                                course_basics=content.get_course_basics(course),
                                assignment_basics=content.get_assignment_basics(course, assignment), error="start",
                                start_date=assignment_details["start_date"].strftime("%c"), user_info=user_info)
                elif assignment_details["start_date"] and assignment_details["start_date"] > curr_datetime:
                    self.render("unavailable_assignment.html", courses=content.get_courses(), assignments=content.get_assignments(course), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), error="start", start_date=assignment_details["start_date"].strftime("%c"), user_info=user_info)
                elif assignment_details["due_date"] and assignment_details["due_date"] < curr_datetime and not assignment_details["allow_late"] and not assignment_details["view_answer_late"]:
                    self.render("unavailable_assignment.html", courses=content.get_courses(), assignments=content.get_assignments(course), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), error="due", due_date=assignment_details["due_date"].strftime("%c"), user_info=user_info)
                else:
                    self.render("assignment.html", courses=content.get_courses(False), assignments=content.get_assignments(course, False), exercises=content.get_exercises(course, assignment, False), exercise_statuses=content.get_exercise_statuses(course, assignment, user_info["user_id"]), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), assignment_details=assignment_details, curr_datetime=curr_datetime, start_time=start_time, user_info=user_info)

            except Exception as inst:
                render_error(self, traceback.format_exc())

    def post(self, course, assignment):
        try:
            show = self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course)
            user_info = self.get_user_info()
            start_time = self.get_body_argument("start_time")
            content.set_user_assignment_start_time(course, assignment, user_info["user_id"], start_time)

            self.render("assignment.html", courses=content.get_courses(show), assignments=content.get_assignments(course, show), exercises=content.get_exercises(course, assignment, show), exercise_statuses=content.get_exercise_statuses(course, assignment, user_info["user_id"]), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), assignment_details=content.get_assignment_details(course, assignment, True), curr_datetime=datetime.datetime.now(), start_time=content.get_user_assignment_start_time(course, assignment, user_info["user_id"]), user_info=user_info)
        except Exception as inst:
            render_error(self, traceback.format_exc())

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

            if assignment_details["has_start_date"]:
                start_date = self.get_body_argument("start_date_picker").strip()
                if start_date == "None":
                    start_date = None
                else:
                    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S.%fZ')
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
                    due_date = datetime.datetime.strptime(due_date, '%Y-%m-%dT%H:%M:%S.%fZ')
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
                            #if not re.match('^[a-zA-Z0-9()\s\"\-]*$', title):
                            #    result = "Error: The title can only contain alphanumeric characters, spaces, hyphens, and parentheses."
                            #else:
                            #content.specify_assignment_basics(assignment_basics, assignment_basics["title"], assignment_basics["visible"])
                            content.specify_assignment_details(assignment_details, assignment_details["introduction"], None, datetime.datetime.now(), assignment_details["start_date"], assignment_details["due_date"], assignment_details["allow_late"], assignment_details["late_percent"], assignment_details["view_answer_late"], assignment_details["enable_help_requests"], assignment_details["has_timer"], assignment_details["hour_timer"], assignment_details["minute_timer"], assignment_details["access_restricted"])
                            assignment = content.save_assignment(assignment_basics, assignment_details)

            percentage_options = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
            hour_options = list(range(13))
            minute_options = list(range(61))

            self.render("edit_assignment.html", courses=content.get_courses(), assignments=content.get_assignments(course), exercises=content.get_exercises(course, assignment), exercise_statuses=content.get_exercise_statuses(course, assignment, self.get_user_info()["user_id"]), course_basics=content.get_course_basics(course), assignment_basics=assignment_basics, assignment_details=assignment_details, percentage_options=percentage_options, hour_options=hour_options, minute_options=minute_options, result=result, user_info=self.get_user_info())

        except Exception as inst:
            render_error(self, traceback.format_exc())

class CopyAssignmentHandler(BaseUserHandler):
    def post(self, course, assignment):
        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                self.render("permissions.html")
                return

            new_course_id = self.get_body_argument("new_course_id")
            content.copy_assignment(course, assignment, new_course_id)
            assignment_basics = content.get_assignment_basics(course, assignment)

            self.render("assignment_admin.html", courses=content.get_courses(True), assignments=content.get_assignments(course, True), exercises=content.get_exercises(course, assignment, True), exercise_statuses=content.get_exercise_statuses(course, assignment, self.get_user_info()["user_id"]), course_basics=content.get_course_basics(course), assignment_basics=assignment_basics, assignment_details=content.get_assignment_details(course, assignment, True), course_options=[x[1] for x in content.get_courses() if str(x[0]) != course], user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course), download_file_name=get_scores_download_file_name(assignment_basics))

        except Exception as inst:
            render_error(self, traceback.format_exc())

class DeleteAssignmentHandler(BaseUserHandler):
    def post(self, course, assignment):
        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                self.render("permissions.html")
                return

            content.delete_assignment(content.get_assignment_basics(course, assignment))
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DeleteAssignmentSubmissionsHandler(BaseUserHandler):
    def post(self, course, assignment):
        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                self.render("permissions.html")
                return

            content.delete_assignment_submissions(content.get_assignment_basics(course, assignment))
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ExerciseHandler(BaseUserHandler):
    def get(self, course, assignment, exercise):
        try:
            assignment_details = content.get_assignment_details(course, assignment)

            if not self.is_administrator() and not self.is_instructor_for_course(course) and not self.is_assistant_for_course(course) and assignment_details["has_timer"]:
                start_time = content.get_user_assignment_start_time(course, assignment, self.get_user_id())

                if not start_time or content.has_user_assignment_start_timer_ended(course, assignment, start_time):
                    if not assignment_details["due_date"] or assignment_details["due_date"] > datetime.datetime.now():
                        self.render("timer_error.html", user_info=content.get_user_info(self.get_user_id()))
                        return

            show = self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course)
            exercises = content.get_exercises(course, assignment, show)
            exercise_details = content.get_exercise_details(course, assignment, exercise, format_content=True)
            back_end = settings_dict["back_ends"][exercise_details["back_end"]]
            next_prev_exercises = content.get_next_prev_exercises(course, assignment, exercise, exercises)

            self.render("exercise.html", courses=content.get_courses(show), assignments=content.get_assignments(course, show), exercises=exercises, course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), assignment_details=content.get_assignment_details(course, assignment), exercise_basics=content.get_exercise_basics(course, assignment, exercise), exercise_details=exercise_details, exercise_statuses=content.get_exercise_statuses(course, assignment, self.get_user_id()), assignment_options=[x[1] for x in content.get_assignments(course) if str(x[0]) != assignment], curr_datetime=datetime.datetime.now(), next_exercise=next_prev_exercises["next"], prev_exercise=next_prev_exercises["previous"], code_completion_path=back_end["code_completion_path"], back_end_description=back_end["description"], num_submissions=content.get_num_submissions(course, assignment, exercise, self.get_user_id()), domain=settings_dict['domain'], start_time=content.get_user_assignment_start_time(course, assignment, self.get_user_id()), help_request=content.get_help_request(course, assignment, exercise, self.get_user_id()), user_info=self.get_user_info(), user_id=self.get_user_id(), student_id=self.get_user_id(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course))

        except Exception as inst:
            render_error(self, traceback.format_exc())

class EditExerciseHandler(BaseUserHandler):
    def get(self, course, assignment, exercise):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                exercises = content.get_exercises(course, assignment)
                exercise_details = content.get_exercise_details(course, assignment, exercise)
                exercise_details["expected_text_output"] = format_output_as_html(exercise_details["expected_text_output"])

                self.render("edit_exercise.html", courses=content.get_courses(), assignments=content.get_assignments(course), exercises=exercises, exercise_statuses=content.get_exercise_statuses(course, assignment, self.get_user_info()["user_id"]), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), exercise_basics=content.get_exercise_basics(course, assignment, exercise), exercise_details=exercise_details, json_files=escape_json_string(json.dumps(exercise_details["data_files"])), next_prev_exercises=content.get_next_prev_exercises(course, assignment, exercise, exercises), code_completion_path=settings_dict["back_ends"][exercise_details["back_end"]]["code_completion_path"], back_ends=sort_nicely(settings_dict["back_ends"].keys()), result=None, user_info=self.get_user_info())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course, assignment, exercise):
        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                self.render("permissions.html")
                return

            exercise_basics = content.get_exercise_basics(course, assignment, exercise)
            exercise_details = content.get_exercise_details(course, assignment, exercise)

            exercise_basics["title"] = self.get_body_argument("title").strip() #required
            exercise_basics["visible"] = self.get_body_argument("is_visible") == "Yes"
            exercise_details["instructions"] = self.get_body_argument("instructions").strip().replace("\r", "") #required
            exercise_details["back_end"] = self.get_body_argument("back_end")
            exercise_details["output_type"] = self.get_body_argument("output_type")
            exercise_details["answer_code"] = self.get_body_argument("answer_code_text").strip().replace("\r", "") #required (usually)
            exercise_details["answer_description"] = self.get_body_argument("answer_description").strip().replace("\r", "")
            exercise_details["hint"] = self.get_body_argument("hint").strip().replace("\r", "")
            exercise_details["max_submissions"] = int(self.get_body_argument("max_submissions"))
            exercise_details["starter_code"] = self.get_body_argument("starter_code_text").strip().replace("\r", "")
            exercise_details["test_code"] = self.get_body_argument("test_code_text").strip().replace("\r", "")
            exercise_details["credit"] = self.get_body_argument("credit").strip().replace("\r", "")
            exercise_details["show_expected"] = self.get_body_argument("show_expected") == "Yes"
            exercise_details["show_test_code"] = self.get_body_argument("show_test_code") == "Yes"
            exercise_details["show_answer"] = self.get_body_argument("show_answer") == "Yes"
            exercise_details["show_student_submissions"] = self.get_body_argument("show_student_submissions") == "Yes"

            old_files = self.get_body_argument("file_container")
            new_files = self.request.files
            if old_files and old_files != "{}":
                old_files = json.loads(old_files)
                exercise_details["data_files"] = old_files
            else:
                exercise_details["data_files"] = {}

            result = "Success: The exercise was saved!"

            any_response_counts = exercise_details["back_end"] == "any_response"

            if exercise_basics["title"] == "" or exercise_details["instructions"] == "" or (not any_response_counts and exercise_details["answer_code"] == ""):
                result = "Error: One of the required fields is missing."
            else:
                if content.has_duplicate_title(content.get_exercises(course, assignment), exercise_basics["id"], exercise_basics["title"]):
                    result = "Error: An exercise with that title already exists in this assignment."
                else:
                    if len(exercise_basics["title"]) > 80:
                        result = "Error: The title cannot exceed 80 characters."
                    else:
                        #if not re.match('^[a-zA-Z0-9()\s\"\-]*$', exercise_basics["title"]):
                        #    result = "Error: The title can only contain alphanumeric characters, spaces, hyphens, and parentheses."
                        #else:
                            if new_files:
                                data_files = {}
                                total_size = 0

                                #create data_files dictionary
                                for fileInput, fileContents in new_files.items():
                                    for i in range(len(fileContents)):
                                        data_files[fileContents[i]["filename"]] = fileContents[i]["body"].decode("utf-8")
                                        total_size += len(fileContents[i]["body"])

                                exercise_details["data_files"].update(data_files)

                                # Make sure total file size is not larger than 10 MB across all files.
                                if total_size > 10 * 1024 * 1024:
                                    result = f"Error: Your total file size is too large ({total_size} bytes)."

                            if not result.startswith("Error:"):
                                content.specify_exercise_basics(exercise_basics, exercise_basics["title"], exercise_basics["visible"])
                                content.specify_exercise_details(exercise_details, exercise_details["instructions"], exercise_details["back_end"], exercise_details["output_type"], exercise_details["answer_code"], exercise_details["answer_description"], exercise_details["hint"], exercise_details["max_submissions"], exercise_details["starter_code"], exercise_details["test_code"], exercise_details["credit"], exercise_details["data_files"], exercise_details["show_expected"], exercise_details["show_test_code"], exercise_details["show_answer"], exercise_details["show_student_submissions"], "", "", None, datetime.datetime.now())

                                text_output, image_output = exec_code(settings_dict, exercise_details["answer_code"], exercise_basics, exercise_details)

                                if not any_response_counts and text_output == "" and image_output == "":
                                    result = f"Error: No output was produced."
                                else:
                                    exercise_details["expected_text_output"] = text_output.strip()
                                    exercise_details["expected_image_output"] = image_output
                                    exercise = content.save_exercise(exercise_basics, exercise_details)

                                    exercise_basics = content.get_exercise_basics(course, assignment, exercise)
                                    exercise_details = content.get_exercise_details(course, assignment, exercise)
                                    exercise_details["expected_text_output"] = format_output_as_html(text_output)

            exercises = content.get_exercises(course, assignment)
            self.render("edit_exercise.html", courses=content.get_courses(), assignments=content.get_assignments(course), exercises=exercises, exercise_statuses=content.get_exercise_statuses(course, assignment, self.get_user_info()["user_id"]), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), exercise_basics=exercise_basics, exercise_details=exercise_details, json_files=escape_json_string(json.dumps(exercise_details["data_files"])), next_prev_exercises=content.get_next_prev_exercises(course, assignment, exercise, exercises), code_completion_path=settings_dict["back_ends"][exercise_details["back_end"]]["code_completion_path"], back_ends=sort_nicely(settings_dict["back_ends"].keys()), result=result, user_info=self.get_user_info())
        except ConnectionError as inst:
            render_error(self, "The front-end server was unable to contact the back-end server.")
        except ReadTimeout as inst:
            render_error(self, f"Your solution timed out after {settings_dict['back_ends'][exercise_details['back_end']]['timeout_seconds']} seconds.")
        except Exception as inst:
            render_error(self, traceback.format_exc())

class CreateVideoExerciseHandler(BaseUserHandler):
    def post(self, course, assignment):
        response_dict = {"message": ""}

        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                response_dict["message"] = "You do not have permissions to perform this operation."
                return

            exercise_basics = content.get_exercise_basics(course, assignment, None)
            exercise_details = content.get_exercise_details(course, assignment, None)

            exercise_basics["title"] = self.get_body_argument("title")
            exercise_details["instructions"] = self.get_body_argument("instructions")
            exercise_details["back_end"] = "any_response"
            created_date = datetime.datetime.now()
            exercise_details["date_updated"] = created_date
            exercise_details["date_created"] = created_date

            exercise = content.save_exercise(exercise_basics, exercise_details)
        except Exception as inst:
            response_dict["message"] = traceback.format_exc()

        self.write(json.dumps(response_dict));

class MoveExerciseHandler(BaseUserHandler):
    def post(self, course, assignment, exercise):
        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                self.render("permissions.html")
                return

            new_assignment_id = self.get_body_argument("new_assignment_id")
            content.move_exercise(course, assignment, exercise, new_assignment_id)

            assignment_basics = content.get_assignment_basics(course, new_assignment_id)
            out_file = f"Assignment_{new_assignment_id}_Scores.csv"

            self.render("assignment_admin.html", courses=content.get_courses(True), assignments=content.get_assignments(course, True), exercises=content.get_exercises(course, new_assignment_id, True), exercise_statuses=content.get_exercise_statuses(course, new_assignment_id, self.get_user_info()["user_id"]), course_basics=content.get_course_basics(course), assignment_basics=assignment_basics, assignment_details=content.get_assignment_details(course, new_assignment_id, True), download_file_name=get_scores_download_file_name(assignment_basics), course_options=[x[1] for x in content.get_courses() if str(x[0]) != course], user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), out_file=out_file)
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DeleteExerciseHandler(BaseUserHandler):
    def post(self, course, assignment, exercise):
        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                self.render("permissions.html")
                return

            content.delete_exercise(content.get_exercise_basics(course, assignment, exercise))
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DeleteExerciseSubmissionsHandler(BaseUserHandler):
    def post(self, course, assignment, exercise):
        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                self.render("permissions.html")
                return

            content.delete_exercise_submissions(content.get_exercise_basics(course, assignment, exercise))
        except Exception as inst:
            render_error(self, traceback.format_exc())

class RunCodeHandler(BaseUserHandler):
    async def post(self, course, assignment, exercise):
        out_dict = {"text_output": "", "image_output": ""}

        try:
            code = self.get_body_argument("user_code").replace("\r", "")
            exercise_basics = content.get_exercise_basics(course, assignment, exercise)
            exercise_details = content.get_exercise_details(course, assignment, exercise)

            text_output, image_output = exec_code(settings_dict, code, exercise_basics, exercise_details, request=None)

            out_dict["text_output"] = format_output_as_html(text_output)
            out_dict["image_output"] = image_output
        except ConnectionError as inst:
            out_dict["text_output"] = "The front-end server was unable to contact the back-end server."
        except ReadTimeout as inst:
            out_dict["text_output"] = f"Your solution timed out after {settings_dict['back_ends'][exercise_details['back_end']]['timeout_seconds']} seconds."
        except Exception as inst:
            out_dict["text_output"] = format_output_as_html(traceback.format_exc())

        self.write(json.dumps(out_dict))

class SubmitHandler(BaseUserHandler):
    async def post(self, course, assignment, exercise):
        out_dict = {"text_output": "", "image_output": "", "diff": "", "passed": False, "submission_id": ""}

        try:
            user_id = self.get_user_id()
            code = self.get_body_argument("user_code").replace("\r", "")
            exercise_basics = content.get_exercise_basics(course, assignment, exercise)
            exercise_details = content.get_exercise_details(course, assignment, exercise)
            assignment_details = content.get_assignment_details(course, assignment)

            text_output, image_output = exec_code(settings_dict, code, exercise_basics, exercise_details, self.request)
            diff, passed = check_exercise_output(exercise_details, text_output, image_output)

            out_dict["text_output"] = format_output_as_html(text_output)
            out_dict["image_output"] = image_output
            out_dict["diff"] = format_output_as_html(diff)
            out_dict["passed"] = passed
            out_dict["submission_id"] = content.save_submission(course, assignment, exercise, user_id, code, text_output, image_output, passed)

            exercise_score = content.get_exercise_score(course, assignment, exercise, user_id)
            new_score = content.calc_exercise_score(assignment_details, passed)
            if (not exercise_score or exercise_score < new_score):
                content.save_exercise_score(course, assignment, exercise, user_id, new_score)

        except ConnectionError as inst:
            out_dict["text_output"] = "The front-end server was unable to contact the back-end server."
            out_dict["passed"] = False
        except ReadTimeout as inst:
            out_dict["text_output"] = f"Your solution timed out after {settings_dict['back_ends'][exercise_details['back_end']]['timeout_seconds']} seconds."
            out_dict["passed"] = False
        except Exception as inst:
            out_dict["text_output"] = format_output_as_html(traceback.format_exc())
            out_dict["passed"] = False

        self.write(json.dumps(out_dict))

class GetSubmissionHandler(BaseUserHandler):
    def get(self, course, assignment, exercise, student_id, submission_id):
        try:
            exercise_details = content.get_exercise_details(course, assignment, exercise)
            submission_info = content.get_submission_info(course, assignment, exercise, student_id, submission_id)

            diff, passed = check_exercise_output(exercise_details, submission_info["text_output"], submission_info["image_output"])

            submission_info["diff"] = format_output_as_html(diff)
            submission_info["text_output"] = format_output_as_html(submission_info["text_output"])
        except Exception as inst:
            submission_info["diff"] = ""
            submission_info["text_output"] = format_output_as_html(traceback.format_exc())

        self.write(json.dumps(submission_info))

class GetSubmissionsHandler(BaseUserHandler):
    def get(self, course, assignment, exercise, user_id):
        try:
            submissions = content.get_submissions_basic(course, assignment, exercise, user_id)
        except Exception as inst:
            submissions = []

        self.write(json.dumps(submissions))

class ViewAnswerHandler(BaseUserHandler):
    def get(self, course, assignment, exercise):
        try:
            user = self.get_user_id()
            exercise_details = content.get_exercise_details(course, assignment, exercise, format_content=True)
            back_end = settings_dict["back_ends"][exercise_details["back_end"]]
            self.render("view_answer.html", courses=content.get_courses(), assignments=content.get_assignments(course), exercises=content.get_exercises(course, assignment), course_basics=content.get_course_basics(course), assignment_basics=content.get_assignment_basics(course, assignment), assignment_details=content.get_assignment_details(course, assignment), exercise_basics=content.get_exercise_basics(course, assignment, exercise), exercise_details=exercise_details, exercise_statuses=content.get_exercise_statuses(course, assignment, user), code_completion_path=back_end["code_completion_path"], last_submission=content.get_last_submission(course, assignment, exercise, user), student_submissions=content.get_student_submissions(course, assignment, exercise, user), curr_time=datetime.datetime.now(), format_content=True, user_info=self.get_user_info())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class AddInstructorHandler(BaseUserHandler):
    def get(self, course):
        try:
            if self.is_administrator():
                course_basics = content.get_course_basics(course)
                self.render("add_instructor.html", courses=content.get_courses(), course_basics=course_basics, instructors=content.get_users_from_role(course_basics["id"], "instructor"), result=None, user_info=self.get_user_info())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course):
        try:
            if not self.is_administrator():
                self.render("permissions.html")
                return

            course_basics = content.get_course_basics(course)
            new_instructor = self.get_body_argument("new_inst")

            if content.user_exists(new_instructor):
                if content.is_administrator(new_instructor):
                    result = f"Error: {new_instructor} is already an administrator and can't be given a lower role."
                else:
                    content.add_permissions(course_basics["id"], new_instructor, "instructor")
                    result = f"Success! {new_instructor} is now an instructor for the {course_basics['title']} course."
            else:
                result = f"Error: The user '{new_instructor}' does not exist."

            self.render("add_instructor.html", courses=content.get_courses(), course_basics=course_basics, instructors=content.get_users_from_role(course_basics["id"], "instructor"), result=result, user_info=self.get_user_info())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class RemoveAdminHandler(BaseUserHandler):
    def post(self, user_id):
        try:
            if not self.is_administrator():
                self.render("permissions.html")
                return

            content.remove_permissions(None, user_id, "administrator")
            self.render("profile_courses.html", page="courses", result=None, courses=content.get_courses(), registered_courses=content.get_registered_courses(user_id), user_info=self.get_user_info(), is_administrator=False, is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class RemoveInstructorHandler(BaseUserHandler):
    def post(self, course, old_instructor):
        try:
            if not self.is_administrator():
                self.render("permissions.html")
                return

            if not content.user_has_role(old_instructor, course, "instructor"):
                result = f"Error: {old_instructor} is not an instructor for this course."
            else:
                content.remove_permissions(course, old_instructor, "instructor")
                result = f"Success: {old_instructor} has been removed from the instructor list."

            self.render("profile_instructor.html", page="instructor", tab="manage_instructors", course=content.get_course_basics(course), assignments=content.get_assignments(course), instructors=content.get_users_from_role(course, "instructor"), assistants=content.get_users_from_role(course, "assistant"), registered_students=content.get_registered_students(course), result=result, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course))
        except Exception as inst:
            render_error(self, traceback.format_exc())

class RemoveAssistantHandler(BaseUserHandler):
    def post(self, course, old_assistant):
        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                self.render("permissions.html")
                return

            if not content.user_has_role(old_assistant, course, "assistant"):
                result = f"Error: {old_assistant} is not an assistant for this course."
            else:
                content.remove_permissions(course, old_assistant, "assistant")
                result = f"Success: {old_assistant} has been removed from the instructor assistant list."

            self.render("profile_instructor.html", page="instructor", tab="manage_assistants", course=content.get_course_basics(course), assignments=content.get_assignments(course), instructors=content.get_users_from_role(course, "instructor"), assistants=content.get_users_from_role(course, "assistant"), registered_students=content.get_registered_students(course), result=result, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course))
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ResetTimerHandler(BaseUserHandler):
    async def post(self, course, assignment, user):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                content.reset_user_assignment_start_timer(course, assignment, user)
            else:
                self.render("permissions.html")

        except Exception as inst:
            self.write(traceback.format_exc())

class ViewScoresHandler(BaseUserHandler):
    def get(self, course, assignment):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                assignment_basics = content.get_assignment_basics(course, assignment)

                self.render("view_scores.html", courses=content.get_courses(), course_basics=content.get_course_basics(course), assignments=content.get_assignments(course), assignment_basics=assignment_basics, assignment_details=content.get_assignment_details(course, assignment), exercises=content.get_exercises(course, assignment), exercise_statuses=content.get_exercise_statuses(course, assignment, self.get_user_id()), scores=content.get_assignment_scores(course, assignment), start_times=content.get_all_user_assignment_start_times(course, assignment), curr_datetime=datetime.datetime.now(), download_file_name=get_scores_download_file_name(assignment_basics), user_info=self.get_user_info())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DownloadFileHandler(BaseUserHandler):
    def get(self, course, assignment, exercise, file_name):
        try:
            file_contents = content.get_exercise_details(course, assignment, exercise)["data_files"][file_name]
            self.set_header("Content-type", "application/octet-stream")
            self.set_header("Content-Disposition", "attachment")
            self.write(file_contents)
        except Exception as inst:
            self.write(traceback.format_exc())

class DownloadScoresHandler(BaseUserHandler):
    def get(self, course, assignment):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                csv_text = content.create_scores_text(course, assignment)
                self.set_header('Content-type', "text/csv")
                self.write(csv_text)
            else:
                self.render("permissions.html")
        except Exception as inst:
            self.write(traceback.format_exc())
            #render_error(self, traceback.format_exc())

class DownloadAllScoresHandler(BaseUserHandler):
    def get(self, course):
        course_basics = content.get_course_basics(course)
        descriptor = f"Course_{course_basics['title'].replace(' ', '_')}_Scores"
        temp_dir_path, zip_file_name, zip_file_path = content.create_zip_file_path(descriptor)

        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):

                content.create_export_paths(temp_dir_path, descriptor)

                assignments = content.get_assignments(course)
                for assignment in assignments:
                    file_contents = content.create_scores_text(course, assignment[0])
                    with open(f"{temp_dir_path}/{assignment[0]}.csv", "w") as score_file:
                        score_file.write(file_contents)

                content.zip_export_files(temp_dir_path, zip_file_name, zip_file_path, descriptor)
                zip_bytes = read_file(zip_file_path, "rb")

                self.set_header("Content-type", "application/zip")
                self.set_header("Content-Disposition", f"attachment; filename={zip_file_name}")
                self.write(zip_bytes)
                self.finish()
            else:
                self.render("permissions.html")

        except Exception as inst:
            render_error(self, traceback.format_exc())
        finally:
            content.remove_export_paths(zip_file_path, tmp_dir_path)

class EditScoresHandler(BaseUserHandler):
    def get(self, course, assignment, student_id):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                self.render("edit_scores.html", student_id=student_id, courses=content.get_courses(), course_basics=content.get_course_basics(course), assignments=content.get_assignments(course), assignment_basics=content.get_assignment_basics(course, assignment), exercises=content.get_exercises(course, assignment), exercise_statuses=content.get_exercise_statuses(course, assignment, student_id), result=None, user_info=self.get_user_info())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course, assignment, student_id):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):

                exercise_statuses = content.get_exercise_statuses(course, assignment, student_id)
                result = ""
                for exercise in exercise_statuses:
                    student_score = self.get_body_argument(str(exercise[1]["id"]))
                    if (student_score.isnumeric()):
                        result = f"Success: {student_id}'s scores for this assignment have been updated."
                        content.save_exercise_score(course, assignment, exercise[1]["id"], student_id, int(student_score))
                    else:
                        result = "Error: Newly entered scores must be numeric."

                self.render("edit_scores.html", student_id=student_id, courses=content.get_courses(), course_basics=content.get_course_basics(course), assignments=content.get_assignments(course), assignment_basics=content.get_assignment_basics(course, assignment), exercises=content.get_exercises(course, assignment), exercise_statuses=content.get_exercise_statuses(course, assignment, student_id), result=result, user_info=self.get_user_info())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

class StudentScoresHandler(BaseUserHandler):
    def get(self, course, assignment, student_id):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                self.render("student_scores.html", student_info=content.get_user_info(student_id), courses=content.get_courses(), course_basics=content.get_course_basics(course), assignments=content.get_assignments(course), assignment_basics=content.get_assignment_basics(course, assignment), exercises=content.get_exercises(course, assignment), exercise_statuses=content.get_exercise_statuses(course, assignment, student_id), user_info=self.get_user_info())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

class StudentExerciseHandler(BaseUserHandler):
    def get(self, course, assignment, exercise, student_id):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                exercises = content.get_exercises(course, assignment, True)
                exercise_details = content.get_exercise_details(course, assignment, exercise, format_content=True)
                back_end = settings_dict["back_ends"][exercise_details["back_end"]]
                next_prev_exercises=content.get_next_prev_exercises(course, assignment, exercise, exercises)

                self.render("student_exercise.html", student_info=content.get_user_info(student_id), student_id=student_id, courses=content.get_courses(True), course_basics=content.get_course_basics(course), assignments=content.get_assignments(course, True), assignment_basics=content.get_assignment_basics(course, assignment), exercises=exercises, exercise_basics=content.get_exercise_basics(course, assignment, exercise), exercise_details=exercise_details, next_exercise=next_prev_exercises["next"], exercise_statuses=content.get_exercise_statuses(course, assignment, self.get_user_info()["user_id"]), assignment_options=[x[1] for x in content.get_assignments(course) if str(x[0]) != assignment], code_completion_path=back_end["code_completion_path"], back_end_description=back_end["description"], num_submissions=content.get_num_submissions(course, assignment, exercise, student_id), user_info=self.get_user_info(), user_id=self.get_user_id(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course))
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ExerciseScoresHandler(BaseUserHandler):
    def get(self, course, assignment, exercise):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                self.render("exercise_scores.html", courses=content.get_courses(), course_basics=content.get_course_basics(course), assignments=content.get_assignments(course), assignment_basics=content.get_assignment_basics(course, assignment), exercise_basics=content.get_exercise_basics(course, assignment, exercise), exercise_scores=content.get_exercise_scores(course, assignment, exercise), user_info=self.get_user_info())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ExerciseSubmissionsHandler(BaseUserHandler):
    def get(self, course, assignment, exercise):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                self.render("exercise_submissions.html", courses=content.get_courses(), course_basics=content.get_course_basics(course), assignments=content.get_assignments(course), assignment_basics=content.get_assignment_basics(course, assignment), exercise_basics=content.get_exercise_basics(course, assignment, exercise), exercise_submissions=content.get_exercise_submissions(course, assignment, exercise), user_info=self.get_user_info())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

class HelpRequestsHandler(BaseUserHandler):
    def get(self, course):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                self.render("help_requests.html", courses=content.get_courses(), course_basics=content.get_course_basics(course), assignments=content.get_assignments(course), help_requests=content.get_help_requests(course), user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course))
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

class SubmitHelpRequestHandler(BaseUserHandler):
    def post(self, course, assignment, exercise):
        try:
            user_id = self.get_user_id()
            student_comment = self.get_body_argument("student_comment")
            help_request = content.get_help_request(course, assignment, exercise, user_id)
            if help_request:
                content.update_help_request(course, assignment, exercise, user_id, student_comment)

            else:
                code = self.get_body_argument("user_code").replace("\r", "")

                exercise_basics = content.get_exercise_basics(course, assignment, exercise)
                exercise_details = content.get_exercise_details(course, assignment, exercise)

                text_output, image_output = exec_code(settings_dict, code, exercise_basics, exercise_details, request=None)
                #text_output = format_output_as_html(text_output)

                content.save_help_request(course, assignment, exercise, user_id, code, text_output, image_output, student_comment, datetime.datetime.now())

        except Exception as inst:
            render_error(self, traceback.format_exc())

class ViewHelpRequestsHandler(BaseUserHandler):
    def get(self, course, assignment, exercise, student_id):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                self.render("view_request.html", courses=content.get_courses(), course_basics=content.get_course_basics(course), assignments=content.get_assignments(course), assignment_basics=content.get_assignment_basics(course, assignment), exercises=content.get_exercises(course, assignment), exercise_basics=content.get_exercise_basics(course, assignment, exercise), exercise_details=content.get_exercise_details(course, assignment, exercise), help_request=content.get_help_request(course, assignment, exercise, student_id), exercise_help_requests=content.get_exercise_help_requests(course, assignment, exercise, student_id), result=None, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course))
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post (self, course, assignment, exercise, student_id):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                suggestion = self.get_body_argument("suggestion")
                more_info_needed = self.get_body_argument("more_info_needed") == "More info needed"
                user_id = self.get_user_id()
                if self.is_assistant_for_course(course):
                    content.save_help_request_suggestion(course, assignment, exercise, student_id, suggestion, 0, user_id, None, more_info_needed)
                    result = "Success: suggestion submitted for approval"
                else:
                    help_request = content.get_help_request(course, assignment, exercise, student_id)
                    if help_request["suggester_id"]:
                        suggester_id = help_request["suggester_id"]
                    else:
                        suggester_id = user_id
                    content.save_help_request_suggestion(course, assignment, exercise, student_id, suggestion, 1, suggester_id, user_id, more_info_needed)
                    result = "Success: suggestion saved"

                self.render("view_request.html", courses=content.get_courses(), course_basics=content.get_course_basics(course), assignments=content.get_assignments(course), assignment_basics=content.get_assignment_basics(course, assignment), exercises=content.get_exercises(course, assignment), exercise_basics=content.get_exercise_basics(course, assignment, exercise), exercise_details=content.get_exercise_details(course, assignment, exercise), help_request=content.get_help_request(course, assignment, exercise, student_id), exercise_help_requests=content.get_exercise_help_requests(course, assignment, exercise, student_id), result=result, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course))
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DeleteHelpRequestHandler(BaseUserHandler):
    def post(self, course, assignment, exercise, user_id):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                content.delete_help_request(course, assignment, exercise, user_id)
                self.render("help_requests.html", courses=content.get_courses(), course_basics=content.get_course_basics(course), assignments=content.get_assignments(course), help_requests=content.get_help_requests(course), user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), is_assistant=self.is_assistant_for_course(course))
            else:
                self.render("permissions.html")
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
            if self.is_administrator():
                years, months, days = get_list_of_dates()
                self.render("summarize_logs.html", filter_list = sorted(content.get_root_dirs_to_log()), years=years, months=months, days=days, show_table=False, user_info=self.get_user_info())
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self):
        try:
            if not self.is_administrator():
                self.render("permissions.html")
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

            self.render("summarize_logs.html", filter = filter, filter_list = sorted(content.get_root_dirs_to_log()), years=years, months=months, days=days, log_dict=content.get_log_table_contents(log_file, year, month, day), show_table=True, user_info=self.get_user_info())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class StaticFileHandler(RequestHandler):
    async def get(self, file_name):
        if file_name.endswith(".html"):
            try:
                self.render(file_name)
            except Exception as inst:
                render_error(self, traceback.format_exc())
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
                if not content.user_exists(user_id):
                    # Add static information for test user.
                    user_dict = {'id': user_id, 'email': 'test_user@gmail.com', 'verified_email': True, 'name': 'Test User', 'given_name': 'Test', 'family_name': 'User', 'picture': 'https://vignette.wikia.nocookie.net/simpsons/images/1/15/Capital_City_Goofball.png/revision/latest?cb=20170903212224', 'locale': 'en'}
                    content.add_user(user_id, user_dict)

                self.set_secure_cookie("user_id", user_id, expires_days=30)

                if not target_path:
                    target_path = "/"
                self.redirect(target_path)

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

                        if content.user_exists(user_id):
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

class LogoutHandler(RequestHandler):
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
        try:
            user_info = user_info_var.get()

            if isinstance(user_info, str):
                user_id = user_info
            else:
                user_id = user_info["user_id"]
        except:
            user_id = "-"

        record.user_id = user_id

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
        content.create_database_tables()

        database_version = content.get_database_version()
        code_version = int(read_file("VERSION").rstrip())

        # Check to see whether there is a database migration script (should only be one per version).
        # If so, make a backup copy of the database and then do the migration.
        for v in range(database_version, code_version):
            migration_file_path = f"/migration_scripts/{v}_to_{v + 1}.py"

            run_command("bash /etc/cron.hourly/back_up_database.sh")

            print(f"Checking database status for version {v}...")
            result = run_command(f"python {migration_file_path}")

            if "***NotNeeded***" in result:
                print("Database migration not needed.")
            elif "***Success***" in result:
                print(f"Database successfully migrated to version {v} using {migration_file_path}.")
                content.update_database_version(code_version)
            else:
                print(f"Database migration failed using {migration_file_path} so rolling back...")
                print(result)
                run_command("bash /etc/cron.hourly/restore_database.sh")
                break

        ##for assignment_title in ["18 - Biostatistics - Analyzing proportions"]:
        ##    content.rebuild_exercises(assignment_title)
        ##    content.rerun_submissions(assignment_title)

        server = tornado.httpserver.HTTPServer(application)
        server.bind(int(os.environ['PORT']))
        server.start(int(os.environ['NUM_PROCESSES']))

        client_ip = tornado.httpserver.remote_ip
        user_info_var = contextvars.ContextVar("user_info")
        user_is_administrator_var = contextvars.ContextVar("user_is_administrator")
        user_instructor_courses_var = contextvars.ContextVar("user_instructor_courses")
        user_assistant_courses_var = contextvars.ContextVar("user_assistant_courses")

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
