from distutils.log import debug
import sys, os

from handlers import *

from content import *
import contextvars
from datetime import datetime
import glob
from helper import *
import html
import io
import json
import logging
import re
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
import ui_methods


def make_app():
    app = Application([
        url(r"/", HomeHandler),
        url(r"/assignment/([^/]+)/([^/]+)", AssignmentHandler, name="assignment"),
        url(r"/create_video_exercise/([^/]+)/([^/]+)", CreateVideoExerciseHandler, name="create_video_exercise"),
        url(r"/copy_assignment/([^/]+)/([^/]+)?", CopyAssignmentHandler, name="copy_assignment"),
        url(r"/copy_course/([^/]+)", CopyCourseHandler, name="copy_course"),
        url(r"/copy_exercise/([^/]+)/([^/]+)/([^/]+)?", CopyExerciseHandler, name="copy_exercise"),
        url(r"/course/([^/]+)", CourseHandler, name="course"),
        url(r"/delete_assignment/([^/]+)/([^/]+)?", DeleteAssignmentHandler, name="delete_assignment"),
        url(r"/delete_assignment_submissions/([^/]+)/([^/]+)?", DeleteAssignmentSubmissionsHandler, name="delete_assignment_submissions"),
        url(r"/delete_course/([^/]+)?", DeleteCourseHandler, name="delete_course"),
        url(r"/delete_course_submissions/([^/]+)?", DeleteCourseSubmissionsHandler, name="delete_course_submissions"),
        url(r"/delete_exercise/([^/]+)/([^/]+)/([^/]+)?", DeleteExerciseHandler, name="delete_exercise"),
        url(r"/delete_exercise_submissions/([^/]+)/([^/]+)/([^/]+)?", DeleteExerciseSubmissionsHandler, name="delete_exercise_submissions"),
        url(r"/delete_request/([^/]+)/([^/]+)/([^/]+)/([^/]+)", DeleteHelpRequestHandler, name="delete_request"),
        url(r"/devlogin", DevelopmentLoginHandler, name="devlogin"),
        url(r"/download_course_scores/([^/]+)", DownloadCourseScoresHandler, name="download_course_scores"),
        url(r"/download_file/([^/]+)/([^/]+)/([^/]+)/([^/]+)", DownloadFileHandler, name="download_file"),
        url(r"/download_assignment_scores/([^/]+)/([^/]+)", DownloadAssignmentScoresHandler, name="download_assignment_scores"),
        url(r"/external/(.+)", ExternalSiteHandler, name="external_site"),
        url(r"/edit_assignment/([^/]+)/([^/]+)?", EditAssignmentHandler, name="edit_assignment"),
        url(r"/edit_course/([^/]+)?", EditCourseHandler, name="edit_course"),
        url(r"/edit_exercise/([^/]+)/([^/]+)/([^/]+)?", EditExerciseHandler, name="edit_exercise"),
        url(r"/edit_scores/([^/]+)/([^/]+)/([^/]+)", EditScoresHandler, name="edit_scores"),
        url(r"/exercise/([^/]+)/([^/]+)/([^/]+)", ExerciseHandler, name="exercise"),
        url(r"/exercise_scores/([^/]+)/([^/]+)/([^/]+)", ExerciseScoresHandler, name="exercise_scores"),
        url(r"/exercise_submissions/([^/]+)/([^/]+)/([^/]+)", ExerciseSubmissionsHandler, name="exercise_submissions"),
        url(r"/export_course/([^/]+)?", ExportCourseHandler, name="export_course"),
        url(r"/export_submissions/([^/]+)?", ExportSubmissionsHandler, name="export_submissions"),
        url(r"/get_partner_id/([^/]+)/([^/]+)", GetPartnerIDHandler, name="get_partner_id"),
        url(r"/get_presubmission/([^/]+)/([^/]+)/([^/]+)/([^/]+)", GetPresubmissionHandler, name="get_presubmission"),
        url(r"/googlelogin", GoogleLoginHandler, name="googlelogin"),
        url(r"/help_requests/([^/]+)", HelpRequestsHandler, name="help_requests"),
        url(r"/login", CASLoginHandler, name="caslogin"),
        url(r"/logout", LogoutHandler, name="logout"),
        url(r"/move_exercise/([^/]+)/([^/]+)/([^/]+)?", MoveExerciseHandler, name="move_exercise"),
        url(r"/profile/admin/([^/]+)", ProfileAdminHandler, name="profile_admin"),
        url(r"/profile/courses/([^/]+)", ProfileCoursesHandler, name="profile_courses"),
        url(r"/profile/consent_forms/([^/]+)", ConsentFormsHandler, name="consent_forms"),
        url(r"/profile/help_requests", ProfileHelpRequestsHandler, name="profile_help_requests"),
        url(r"/profile/instructor/([^/]+)/([^/]+)", ProfileInstructorHandler, name="profile_instructor"),
        url(r"/profile/instructor_select_course/([^/]+)", ProfileInstructorSelectCourseHandler, name="profile_instructor_select_course"),
        url(r"/profile/manage_users", ProfileManageUsersHandler, name="profile_manage_users"),
        url(r"/profile/personal_info/([^/]+)", ProfilePersonalInfoHandler, name="profile_personal_info"),
        url(r"/profile/preferences/([^/]+)", ProfilePreferencesHandler, name="profile_preferences"),
        url(r"/profile/student_help_requests", ProfileStudentHelpRequestsHandler, name="profile_student_help_requests"),
        url(r"/remove_admin/([^/]+)", RemoveAdminHandler, name="remove_admin"),
        url(r"/remove_assistant/([^/]+)/([^/]+)", RemoveAssistantHandler, name="remove_assistant"),
        url(r"/remove_instructor/([^/]+)/([^/]+)", RemoveInstructorHandler, name="remove_instructor"),
        url(r"/reset_timer/([^/]+)/([^/]+)/([^/]+)", ResetTimerHandler, name="reset_timer"),
        url(r"/run_code/([^/]+)/([^/]+)/([^/]+)", RunCodeHandler, name="run_code"),
        url(r"/save_presubmission/([^/]+)/([^/]+)/([^/]+)", SavePresubmissionHandler, name="save_presubmission"),
        url(r"/static/(.+)", StaticFileHandler, name="static_file"),
        url(r"/student_exercise/([^/]+)/([^/]+)/([^/]+)/([^/]+)", StudentExerciseHandler, name="student_exercise"),
        url(r"/student_scores/([^/]+)/([^/]+)/([^/]+)", StudentScoresHandler, name="student_scores"),
        url(r"/submit/([^/]+)/([^/]+)/([^/]+)", SubmitHandler, name="submit"),
        url(r"/submit_request/([^/]+)/([^/]+)/([^/]+)", SubmitHelpRequestHandler, name="submit_request"),
        url(r"/summarize_logs", SummarizeLogsHandler, name="summarize_logs"),
        url(r"/test", TestHandler, name="test"),
        url(r"/unregister/([^/]+)/([^/]+)", UnregisterHandler, name="unregister"),
        url(r"/view_instructor_solution/([^/]+)/([^/]+)/([^/]+)", ViewInstructorSolutionHandler, name="view_instructor_solution"),
        url(r"/view_peer_solution/([^/]+)/([^/]+)/([^/]+)", ViewPeerSolutionHandler, name="view_peer_solution"),
        url(r"/view_pp/([^/]+)", ViewPairProgrammingAssignmentsHandler, name="view_pp"),
        url(r"/view_request/([^/]+)/([^/]+)/([^/]+)/([^/]+)", ViewHelpRequestsHandler, name="view_request"),
        url(r"/view_scores/([^/]+)/([^/]+)", ViewScoresHandler, name="view_scores"),
    ],
    autoescape=None,
    debug=('DEBUG' in os.environ),
    ui_methods=ui_methods,
    )

    app.settings['template_path'] = os.path.join(os.path.dirname(__file__), "html")

    return app

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

            file_contents = read_file("static/{}".format(file_name), mode=read_mode)

            self.set_header('Content-type', content_type)
            self.write(file_contents)

if __name__ == "__main__":
    if "PORT" in os.environ and "MPORT" in os.environ:
        application = make_app()

        # root_dir = '/'
        # if 'ROOT' in os.environ:
        #     root_dir = os.environ['ROOT']

        secrets_dict = load_yaml_dict(read_file("secrets/front_end.yaml"))
        application.settings["cookie_secret"] = secrets_dict["cookie"]
        #application.settings["google_oauth"] = {
        #    "key": secrets_dict["google_oauth_key"],
        #    "secret": secrets_dict["google_oauth_secret"]}
        settings_dict = load_yaml_dict(read_file("Settings.yaml"))

        content = Content(settings_dict)

        database_version = content.get_database_version()
        code_version = int(read_file("VERSION").rstrip())

        if database_version != code_version:
            print(f"Current database version: {database_version}")
            print(f"Current code version: {code_version}")

        # Check to see whether there is a database migration script (should only be one per version).
        # If so, make a backup copy of the database and then do the migration.
        for v in range(database_version, code_version):
            migration = f"{v}_to_{v + 1}"
            print(f"Checking database status for version {v+1}...")

            if os.path.isfile(f"migration_scripts/{migration}.py"):
                command = f"python3 migration_scripts/{migration}.py"
            else:
                command = f"python3 migration_scripts/migrate.py {migration}"

            result = run_command(command)

            if "***NotNeeded***" in result:
                print("Database migration not needed.")

                if ((v + 1) == code_version):
                    content.update_database_version(v + 1)
            elif "***Success***" in result:
                print(f"Database successfully migrated to version {v+1}")
                content.update_database_version(v + 1)
            else:
                print(f"Database migration failed for version {v+1}...")
                print(result)
                sys.exit(1)

        if settings_dict["mode"] == "development":
            server = tornado.httpserver.HTTPServer(application)
        else:
            server = tornado.httpserver.HTTPServer(application, ssl_options={
              "certfile": "/certs/cert.crt",
              "keyfile": "/certs/cert.key",
            })

        server.bind(int(os.environ['PORT']))
        server.start(int(os.environ['NUM_PROCESSES']))

        user_info_var = contextvars.ContextVar("user_info")
        user_is_administrator_var = contextvars.ContextVar("user_is_administrator")
        user_instructor_courses_var = contextvars.ContextVar("user_instructor_courses")
        user_assistant_courses_var = contextvars.ContextVar("user_assistant_courses")

        # Set up logging
        if 'DEBUG' not in os.environ:
            options.log_file_prefix = os.path.join("logs/codebuddy.log")
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
