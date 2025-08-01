# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from concurrent_log_handler import ConcurrentRotatingFileHandler
from distutils.log import debug
from content import *
from handlers import *
from helper import *
import logging
import os
import signal
import sys
from tornado.auth import GoogleOAuth2Mixin
import tornado.ioloop
from tornado.web import *
import traceback
import ui_methods

def make_app(settings_dict):
    app = Application(
        [
            url(r"/", HomeHandler, name="home"),
            url(r"/add_admin/([^/]+)", AddAdminHandler, name="add_admin"),
            url(r"/add_assignment_group/([^/]+)/([^/]+)", AddAssignmentGroupHandler, name="add_assignment_group"),
            url(r"/add_assistant/([^/]+)/([^/]+)", AddAssistantHandler, name="add_assistant"),
            url(r"/add_instructor/([^/]+)/([^/]+)", AddInstructorHandler, name="add_instructor"),
            url(r"/answer_question/([^/]+)/([^/]+)/([^/]+)/([^/]+)", AnswerQuestionHandler, name="answer_question"),
            url(r"/ask_virtual_assistant/([^/]+)/([^/]+)/([^/]+)", AskVirtualAssistantHandler, name="ask_virtual_assistant"),
            url(r"/assignment/([^/]+)/([^/]+)", AssignmentHandler, name="assignment"),
            url(r"/available", AvailableCoursesHandler, name="available"),
            url(r"/caslogin", CASLoginHandler, name="caslogin"),
            url(r"/create_video_exercise/([^/]+)/([^/]+)", CreateVideoExerciseHandler, name="create_video_exercise"),
            url(r"/copy_assignment/([^/]+)/([^/]+)?", CopyAssignmentHandler, name="copy_assignment"),
            url(r"/copy_course/([^/]+)", CopyCourseHandler, name="copy_course"),
            url(r"/copy_exercise/([^/]+)/([^/]+)/([^/]+)?", CopyExerciseHandler, name="copy_exercise"),
            url(r"/course/([^/]+)", CourseHandler, name="course"),
            url(r"/courses", CoursesHandler, name="courses"),
            url(r"/delete_user/([^/]+)", DeleteUserHandler, name="delete_user"),
            url(r"/delete_assignment/([^/]+)/([^/]+)?", DeleteAssignmentHandler, name="delete_assignment"),
            url(r"/delete_assignment_submissions/([^/]+)/([^/]+)?", DeleteAssignmentSubmissionsHandler, name="delete_assignment_submissions"),
            url(r"/delete_course/([^/]+)?", DeleteCourseHandler, name="delete_course"),
            url(r"/delete_course_submissions/([^/]+)?", DeleteCourseSubmissionsHandler, name="delete_course_submissions"),
            url(r"/delete_exercise/([^/]+)/([^/]+)/([^/]+)?", DeleteExerciseHandler, name="delete_exercise"),
            url(r"/delete_exercise_submissions/([^/]+)/([^/]+)/([^/]+)?", DeleteExerciseSubmissionsHandler, name="delete_exercise_submissions"),
            url(r"/delete_question/([^/]+)", DeleteQuestionHandler, name="delete_question"),
            url(r"/devlogin", DevelopmentLoginHandler, name="devlogin"),
            url(r"/diff", DiffHandler, name="diff"),
            url(r"/download_assignment_scores/([^/]+)/([^/]+)", DownloadAssignmentScoresHandler, name="download_assignment_scores"),
            url(r"/download_course_scores/([^/]+)", DownloadCourseScoresHandler, name="download_course_scores"),
            url(r"/download_file/([^/]+)/([^/]+)/([^/]+)/([^/]+)", DownloadFileHandler, name="download_file"),
            url(r"/download_submissions_student/([^/]+)", DownloadSubmissionsStudentHandler, name="download_submissions_student"),
            url(r"/edit_assignment/([^/]+)/([^/]+)?", EditAssignmentHandler, name="edit_assignment"),
            url(r"/edit_course/([^/]+)?", EditCourseHandler, name="edit_course"),
            url(r"/edit_exercise/([^/]+)/([^/]+)/([^/]+)?", EditExerciseHandler, name="edit_exercise"),
            url(r"/edit_mc_exercise/([^/]+)/([^/]+)/([^/]+)?", EditMultipleChoiceExerciseHandler, name="edit_mc_exercise"),
            url(r"/exercise/([^/]+)/([^/]+)/([^/]+)", ExerciseHandler, name="exercise"),
            url(r"/exercise_submissions/([^/]+)/([^/]+)/([^/]+)", ExerciseSubmissionsHandler, name="exercise_submissions"),
            url(r"/export_assignment/([^/]+)/([^/]+)", ExportAssignmentHandler, name="export_assignment"),
            url(r"/external/([^/]+)/([^/]+)/(.+)", ExternalSiteHandler, name="external"),
            url(r"/generate_security_codes/([^/]+)", GenerateSecurityCodesHandler, name="generate_security_codes"),
            url(r"/get_partner_id/([^/]+)/([^/]+)", GetPartnerIDHandler, name="get_partner_id"),
            url(r"/googlelogin", GoogleLoginHandler, name="googlelogin"),
            url(r"/import_assignment/([^/]+)", ImportAssignmentHandler, name="import_assignment"),
            url(r"/is_taking_restricted_assignment/([^/]+)/([^/]+)", IsTakingRestrictedAssignmentHandler, name="is_taking_restricted_assignment"),
            url(r"/login", LoginHandler, name="login"),
            url(r"/logout", LogoutHandler, name="logout"),
            url(r"/manage_admins", ManageAdminsHandler, name="manage_admins"),
            url(r"/manage_assignment_groups/([^/]+)", ManageAssignmentGroupsHandler, name="manage_assignment_groups"),
            url(r"/manage_assistants/([^/]+)", ManageAssistantsHandler, name="manage_assistants"),
            url(r"/manage_instructors/([^/]+)", ManageInstructorsHandler, 
            name="manage_instructors"),
            url(r"/manage_questions/([^/]+)", ManageQuestionsHandler, name="manage_questions"),
            url(r"/manage_users", ManageUsersHandler, name="manage_users"),
            url(r"/move_assignment/([^/]+)/([^/]+)", MoveAssignmentHandler, name="move_assignment"),
            url(r"/move_exercise/([^/]+)/([^/]+)/([^/]+)?", MoveExerciseHandler, name="move_exercise"),
            url(r"/my_profile/([^/]+)", MyProfileHandler, name="my_profile"),
            url(r"/preferences/([^/]+)", PreferencesHandler, name="preferences"),
            url(r"/register/([^/]+)/([^/]+)/([^/]+)", RegisterHandler, name="register"),
            url(r"/remove_admin", RemoveAdminHandler, name="remove_admin"),
            url(r"/remove_assignment_group/([^/]+)/([^/]+)", RemoveAssignmentGroupHandler, name="remove_assignment_group"),
            url(r"/remove_assistant/([^/]+)/([^/]+)", RemoveAssistantHandler, name="remove_assistant"),
            url(r"/remove_instructor/([^/]+)/([^/]+)", RemoveInstructorHandler, name="remove_instructor"),
            url(r"/resave_exercises/([^/]+)/([^/]+)", ResaveExercisesHandler, name="resave_exercises"),
            url(r"/reset_timer/([^/]+)/([^/]+)/([^/]+)", ResetTimerHandler, name="reset_timer"),
            url(r"/run_code/([^/]+)/([^/]+)/([^/]+)", RunCodeHandler, name="run_code"),
            url(r"/run_code_sandbox/([^/]+)/([^/]+)/([^/]+)/([^/]+)", RunCodeSandboxHandler, name="run_code_sandbox"),
            url(r"/save_presubmission/([^/]+)/([^/]+)/([^/]+)", SavePresubmissionHandler, name="save_presubmission"),
            url(r"/save_thumb_status/([^/]+)/([^/]+)/([^/]+)/([^/]+)/([^/]+)", SaveThumbStatusHandler, name="save_thumb_status"),
            url(r"/save_question/([^/]+)/([^/]+)/([^/]+)/([^/]+)", SaveQuestionHandler, name="save_question"),
            url(r"/static/(.+)", StaticFileHandler, name="static_file"),
            url(r"/student_exercise/([^/]+)/([^/]+)/([^/]+)/([^/]+)", StudentExerciseHandler, name="student_exercise"),
            url(r"/student_score/([^/]+)/([^/]+)/([^/]+)/([^/]+)/([^/]+)", StudentScoreHandler, name="student_score"),
            url(r"/submit/([^/]+)/([^/]+)/([^/]+)", SubmitHandler, name="submit"),
            url(r"/summarize_logs", SummarizeLogsHandler, name="summarize_logs"),
            url(r"/test", TestHandler, name="test"),
            url(r"/unregister/([^/]+)/([^/]+)", UnregisterHandler, name="unregister"),
            url(r"/verify_security_code/([^/]+)/([^/]+)", VerifySecurityCodeHandler, name="verify_security_code"),
            url(r"/view_assignment_scores/([^/]+)/([^/]+)", ViewAssignmentScoresHandler, name="view_assignment_scores"),
            url(r"/view_at_risk_students/([^/]+)/([^/]+)", ViewAtRiskStudentsHandler, name="view_at_risk_students"),
            url(r"/view_exercise_scores/([^/]+)/([^/]+)/([^/]+)", ViewExerciseScoresHandler, name="view_exercise_scores"),
            url(r"/view_instructor_solution/([^/]+)/([^/]+)/([^/]+)", ViewInstructorSolutionHandler, name="view_instructor_solution"),
            url(r"/view_peer_solution/([^/]+)/([^/]+)/([^/]+)", ViewPeerSolutionHandler, name="view_peer_solution"),
            url(r"/view_security_codes/([^/]+)/([^/]+)", ViewSecurityCodesHandler, name="view_security_codes"),
            url(r"/view_student_assignment_scores/([^/]+)/([^/]+)/([^/]+)", ViewStudentAssignmentScoresHandler, name="view_student_assignment_scores"),
            url(r"/view_student_assignments_scores/([^/]+)/([^/]+)", ViewStudentAssignmentsScoresHandler, name="view_student_assignments_scores"),
            url(r"/view_students/([^/]+)", ViewStudentsHandler, name="view_students"),
        ],
        autoescape=None,
        debug=(int(settings_dict["f_num_processes"]) == 1 and 'DEBUG' in os.environ and os.environ['DEBUG'] == 'true'),
        ui_methods=ui_methods
    )
    # Debugging doesn't seem to work on MacOS when running with two processes (https://github.com/tornadoweb/tornado/issues/2426)

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
            elif file_name.endswith(".ttf"):
                content_type = "font/ttf"
                read_mode = "rb"
            elif file_name.endswith(".webmanifest"):
                content_type = "application/json"

            file_contents = read_file("static/{}".format(file_name), mode=read_mode)

            self.set_header('Content-type', content_type)
            self.write(file_contents)

# Define the function you want to run on server exit
def on_exit():
    print("Server is shutting down.")

    content.final_commit()
    content.close()

    # Stop the I/O loop gracefully
    tornado.ioloop.IOLoop.instance().stop()

# Set up signal handling to catch termination signals
def handle_signal(sig, frame):
    tornado.ioloop.IOLoop.instance().add_callback_from_signal(on_exit)

if __name__ == "__main__":
    try:
        settings_dict = load_yaml_dict(read_file("../Settings.yaml"))

        content = Content(settings_dict)

        database_version = content.get_database_version()
        code_version = int(read_file("../VERSION").rstrip())

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
                command = f"python3 migration_scripts/migrate.py {migration} {v}"

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

        # Clean some stuff in the database
        content.delete_old_presubmissions()

        application = make_app(settings_dict)

        if settings_dict["mode"] == "development":
            server = tornado.httpserver.HTTPServer(application, max_header_size=1048576)
        else:
            server = tornado.httpserver.HTTPServer(application, max_header_size=1048576, ssl_options={
              "certfile": "/certs/cert.crt",
              "keyfile": "/certs/cert.key",
            })

        secrets_dict = load_yaml_dict(read_file("secrets/front_end.yaml"))
        application.settings["cookie_secret"] = secrets_dict["cookie"]
        application.settings["google_oauth"] = {
           "key": secrets_dict["google_oauth_key"],
           "secret": secrets_dict["google_oauth_secret"]
        }

        application.settings["byu_authentication"] = False
        if "byu_authentication" in secrets_dict:
            application.settings["byu_authentication"] = secrets_dict["byu_authentication"]    

        server.bind(int(settings_dict["f_port"]))
        server.start(int(settings_dict["f_num_processes"]))

        # Set up logging
        log_level = logging.INFO
        if settings_dict["mode"] == "development":
            log_level = logging.DEBUG

        log_file_handler = ConcurrentRotatingFileHandler("logs/codebuddy.log", maxBytes=100*1024*1024, backupCount=10, encoding="utf-8", mode="a")

        logging.basicConfig(
            handlers=[log_file_handler],
            level=log_level,
            format="[%(asctime)s] %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        logger = logging.getLogger('codebuddy_logger')
        logger.addHandler(log_file_handler)

        logging.getLogger('tornado.access').disabled = True
        logging.getLogger("requests").setLevel(logging.DEBUG)

        # Register signals for graceful shutdown
        signal.signal(signal.SIGINT, handle_signal)  # Ctrl+C
        signal.signal(signal.SIGTERM, handle_signal)  # Termination (like in Docker)

        logging.debug(f"Starting on port {settings_dict['f_port']} using {settings_dict['f_num_processes']} processes")
        tornado.ioloop.IOLoop.instance().start()
    except Exception as inst:
        print(traceback.format_exc())
        logging.error(traceback.format_exc())
        sys.exit(1)