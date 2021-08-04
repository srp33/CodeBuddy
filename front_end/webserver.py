from handlers.HomeHandler import *
from handlers.BaseUserHandler import *
from handlers.TestHandler import *
from handlers.ConsentFormsHandler import *
from handlers.ProfileCoursesHandler import *
from handlers.ProfilePersonalInfoHandler import *
from handlers.ProfileAdminHandler import *
from handlers.ProfileSelectCourseHandler import *
from handlers.ProfileInstructorHandler import *
from handlers.ProfileManageUsersHandler import *
from handlers.ProfileHelpRequestsHandler import *
from handlers.ProfileStudentHelpRequestsHandler import *
from handlers.ProfilePreferencesHandler import *
from handlers.UnregisterHandler import *
from handlers.CourseHandler import *
from handlers.EditCourseHandler import *
from handlers.DeleteCourseHandler import *
from handlers.DeleteCourseSubmissionsHandler import *
from handlers.ImportCourseHandler import *
from handlers.ExportCourseHandler import *
from handlers.ExportSubmissionsHandler import *
from handlers.AssignmentHandler import *
from handlers.EditAssignmentHandler import *
from handlers.CopyAssignmentHandler import *
from handlers.DeleteAssignmentHandler import *
from handlers.DeleteAssignmentSubmissionsHandler import *
from handlers.ExerciseHandler import *
from handlers.EditExerciseHandler import *
from handlers.CreateVideoExerciseHandler import *
from handlers.MoveExerciseHandler import *
from handlers.CopyExerciseHandler import *
from handlers.DeleteExerciseHandler import *
from handlers.DeleteExerciseSubmissionsHandler import *
from handlers.CheckPartnersHandler import *
from handlers.RunCodeHandler import *
from handlers.SavePresubmissionHandler import *
from handlers.SubmitHandler import *
from handlers.GetPresubmissionHandler import *
from handlers.GetSubmissionHandler import *
from handlers.GetSubmissionsHandler import *
from handlers.GetTestsHandler import *
from handlers.ViewAnswerHandler import *
from handlers.AddInstructorHandler import *
from handlers.RemoveAdminHandler import *
from handlers.RemoveInstructorHandler import *
from handlers.RemoveAssistantHandler import *
from handlers.ResetTimerHandler import *
from handlers.ViewScoresHandler import *
from handlers.DownloadFileHandler import *
from handlers.DownloadScoresHandler import *
from handlers.DownloadAllScoresHandler import *
from handlers.EditScoresHandler import *
from handlers.StudentScoresHandler import *
from handlers.StudentExerciseHandler import *
from handlers.ExerciseScoresHandler import *
from handlers.ExerciseSubmissionsHandler import *
from handlers.HelpRequestsHandler import *
from handlers.SubmitHelpRequestHandler import *
from handlers.ViewHelpRequestsHandler import *
from handlers.DeleteHelpRequestHandler import *
from handlers.BackEndHandler import *
from handlers.SummarizeLogsHandler import *
from handlers.StaticFileHandler import *
from handlers.DevelopmentLoginHandler import *
from handlers.GoogleLoginHandler import *
from handlers.LogoutHandler import *
from handlers.LoggingFilter import *

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
        url(r"\/profile\/consent_forms\/([^\/]+)", ConsentFormsHandler, name="consent_forms"),
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
        url(r"\/copy_exercise\/([^\/]+)\/([^\/]+)/([^\/]+)?", CopyExerciseHandler, name="copy_exercise"),
        url(r"\/delete_exercise\/([^\/]+)\/([^\/]+)/([^\/]+)?", DeleteExerciseHandler, name="delete_exercise"),
        url(r"\/delete_exercise_submissions\/([^\/]+)\/([^\/]+)/([^\/]+)?", DeleteExerciseSubmissionsHandler, name="delete_exercise_submissions"),
        url(r"\/run_code\/([^\/]+)\/([^\/]+)/([^\/]+)", RunCodeHandler, name="run_code"),
        url(r"\/submit\/([^\/]+)\/([^\/]+)/([^\/]+)", SubmitHandler, name="submit"),
        url(r"\/get_submission\/([^\/]+)\/([^\/]+)/([^\/]+)/([^\/]+)/(\d+)", GetSubmissionHandler, name="get_submission"),
        url(r"\/get_submissions\/([^\/]+)\/([^\/]+)/([^\/]+)/([^\/]+)", GetSubmissionsHandler, name="get_submissions"),
        url(r"\/get_tests\/([^\/]+)\/([^\/]+)/([^\/]+)", GetTestsHandler, name="get_tests"),
        url(r"\/save_presubmission\/([^\/]+)\/([^\/]+)/([^\/]+)", SavePresubmissionHandler, name="save_presubmission"),
        url(r"\/get_presubmission\/([^\/]+)\/([^\/]+)/([^\/]+)/([^\/]+)", GetPresubmissionHandler, name="get_presubmission"),
        url(r"\/check_partners\/([^\/]+)", CheckPartnersHandler, name="check_partners"),
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
        url(r"/test", TestHandler, name="test"),
    ], autoescape=None)

    return app




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
            run_command("bash /etc/cron.hourly/back_up_database.sh")

            migration = f"{v}_to_{v + 1}"
            print(f"Checking database status for version {v+1}...")

            if os.path.isfile(f"/migration_scripts/{migration}.py"):
                command = f"python /migration_scripts/{migration}.py"
            else:
                command = f"python /migration_scripts/migrate.py {migration}"

            result = run_command(command)

            if "***NotNeeded***" in result:
                print("Database migration not needed.")
            elif "***Success***" in result:
                print(f"Database successfully migrated to version {v+1}.")
                content.update_database_version(code_version)
            else:
                print(f"Database migration failed for verson {v+1}, so rolling back...")
                print(result)
                run_command("bash /etc/cron.hourly/restore_database.sh")
                sys.exit(1)

        server = tornado.httpserver.HTTPServer(application)
        server.bind(int(os.environ['PORT']))
        server.start(int(os.environ['NUM_PROCESSES']))

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
