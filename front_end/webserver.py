from helper import *
from content import *
import json
import re
import tornado.ioloop
from tornado.web import *
import traceback
import urllib.request
import uuid

def make_app():
    return Application([
        url(r"/", HomeHandler),
        url(r"\/course\/([^\/]+)", CourseHandler, name="course"),
        url(r"\/edit_course\/([^\/]+)?", EditCourseHandler, name="edit_course"),
        url(r"\/delete_course\/([^\/]+)?", DeleteCourseHandler, name="delete_course"),
        url(r"\/import_course", ImportCourseHandler, name="import_course"),
        url(r"\/export_course\/([^\/]+)?", ExportCourseHandler, name="export_course"),
        url(r"\/assignment\/([^\/]+)\/([^\/]+)", AssignmentHandler, name="assignment"),
        url(r"\/edit_assignment\/([^\/]+)\/([^\/]+)?", EditAssignmentHandler, name="edit_assignment"),
        url(r"\/delete_assignment\/([^\/]+)\/([^\/]+)?", DeleteAssignmentHandler, name="delete_assignment"),
        url(r"\/problem\/([^\/]+)\/([^\/]+)/([^\/]+)", ProblemHandler, name="problem"),
        url(r"\/edit_problem\/([^\/]+)\/([^\/]+)/([^\/]+)?", EditProblemHandler, name="edit_problem"),
        url(r"\/delete_problem\/([^\/]+)\/([^\/]+)/([^\/]+)?", DeleteProblemHandler, name="delete_problem"),
        url(r"\/check_problem\/([^\/]+)\/([^\/]+)/([^\/]+)", CheckProblemHandler, name="check_problem"),
        url(r"\/output_types\/([^\/]+)", OutputTypesHandler, name="output_types"),
        url(r"/static/([^\/]+)", StaticFileHandler, name="static_file"),
        url(r"/data/([^\/]+)\/([^\/]+)/([^\/]+)/([^\/]+)", DataHandler, name="data"),
    ], autoescape=None)

class HomeHandler(RequestHandler):
    def get(self):
        try:
            self.render("home.html", courses=get_courses(show_hidden(self)))
        except Exception as inst:
            render_error(self, traceback.format_exc())

class CourseHandler(RequestHandler):
    def get(self, course):
        try:
            show = show_hidden(self)
            self.render("course.html", courses=get_courses(show), assignments=get_assignments(course, show), course_basics=get_course_basics(course), course_details=get_course_details(course, True))
        except Exception as inst:
            render_error(self, traceback.format_exc())

class EditCourseHandler(RequestHandler):
    def get(self, course):
        try:
            self.render("edit_course.html", courses=get_courses(), assignments=get_assignments(course), course_basics=get_course_basics(course), course_details=get_course_details(course), result=None)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course):
        try:
            #submitted_password = self.get_body_argument("password")
            submitted_password = password

            courses = get_courses()
            course_basics = get_course_basics(course)
            course_basics["title"] = self.get_body_argument("title").strip()
            course_basics["visible"] = self.get_body_argument("is_visible") == "Yes"
            course_details = {"introduction": self.get_body_argument("introduction").strip()}

            if submitted_password == password:
                if course_basics["title"] == "" or course_details["introduction"] == "":
                    result = "Error: Missing title or introduction."
                else:
                    if has_duplicate_title(courses, course, course_basics["title"]):
                        result = "Error: A course with that title already exists."
                    else:
                        if re.search(r"[^\w ]", course_basics["title"]):
                            result = "Error: The title can only contain alphanumeric characters and spaces."
                        else:
                            save_course(course_basics, course_details)
                            course_basics = get_course_basics(course)
                            courses = get_courses()
                            result = "Success: Course information saved!"
            else:
                result = "Error: Invalid password."

            self.render("edit_course.html", courses=courses, assignments=get_assignments(course), course_basics=course_basics, course_details=course_details, result=result)
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DeleteCourseHandler(RequestHandler):
    def get(self, course):
        try:
            self.render("delete_course.html", courses=get_courses(), assignments=get_assignments(course), course_basics=get_course_basics(course), result=None)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course):
        try:
            #submitted_password = self.get_body_argument("password")
            submitted_password = password

            if submitted_password == password:
                delete_course(get_course_basics(course))
                result = "Success: Course deleted."
            else:
                result = "Error: Invalid password."

            self.render("delete_course.html", courses=get_courses(), assignments=get_assignments(course), course_basics=get_course_basics(course), result=result)
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ImportCourseHandler(RequestHandler):
    def get(self):
        try:
            self.render("import_course.html", result=None)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self):
        try:
            submitted_password = password

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

            self.render("import_course.html", result=result)
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ExportCourseHandler(RequestHandler):
    def get(self, course):
        try:
            temp_dir_path = "/tmp/{}".format(create_id())
            zip_file_name = "{}.zip".format(get_course_basics(course)["title"].replace(" ", "_"))
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

class AssignmentHandler(RequestHandler):
    def get(self, course, assignment):
        try:
            show = show_hidden(self)
            self.render("assignment.html", courses=get_courses(show), assignments=get_assignments(course, show), problems=get_problems(course, assignment, show), course_basics=get_course_basics(course), assignment_basics=get_assignment_basics(course, assignment), assignment_details=get_assignment_details(course, assignment, True))
        except Exception as inst:
            render_error(self, traceback.format_exc())

class EditAssignmentHandler(RequestHandler):
    def get(self, course, assignment):
        try:
            self.render("edit_assignment.html", courses=get_courses(), assignments=get_assignments(course), problems=get_problems(course, assignment), course_basics=get_course_basics(course), assignment_basics=get_assignment_basics(course, assignment), assignment_details=get_assignment_details(course, assignment), result=None)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course, assignment):
        try:
            #submitted_password = self.get_body_argument("password")
            submitted_password = password

            assignment_basics = get_assignment_basics(course, assignment)
            assignment_basics["title"] = self.get_body_argument("title").strip()
            assignment_basics["visible"] = self.get_body_argument("is_visible") == "Yes"
            assignment_details = {"introduction": self.get_body_argument("introduction").strip()}

            if submitted_password == password:
                if assignment_basics["title"] == "" or assignment_details["introduction"] == "":
                    result = "Error: Missing title or introduction."
                else:
                    if has_duplicate_title(get_assignments(course), assignment, assignment_basics["title"]):
                        result = "Error: An assignment with that title already exists."
                    else:
                        save_assignment(assignment_basics, assignment_details)
                        assignment_basics = get_assignment_basics(course, assignment)
                        result = "Success: Assignment information saved!"
            else:
                result = "Error: Invalid password."

            self.render("edit_assignment.html", courses=get_courses(), assignments=get_assignments(course), problems=get_problems(course, assignment), course_basics=get_course_basics(course), assignment_basics=assignment_basics, assignment_details=assignment_details, result=result)
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DeleteAssignmentHandler(RequestHandler):
    def get(self, course, assignment):
        try:
            self.render("delete_assignment.html", courses=get_courses(), assignments=get_assignments(course), problems=get_problems(course, assignment), course_basics=get_course_basics(course), assignment_basics=get_assignment_basics(course, assignment), result=None)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course, assignment):
        try:
            #submitted_password = self.get_body_argument("password")
            submitted_password = password

            if submitted_password == password:
                delete_assignment(get_assignment_basics(course, assignment))
                result = "Success: Assignment deleted."
            else:
                result = "Error: Invalid password."

            self.render("delete_assignment.html", courses=get_courses(), assignments=get_assignments(course), problems=get_problems(course, assignment), course_basics=get_course_basics(course), assignment_basics=get_assignment_basics(course, assignment), result=result)
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ProblemHandler(RequestHandler):
    def get(self, course, assignment, problem):
        try:
            show = show_hidden(self)
            problems = get_problems(course, assignment, show)

            self.render("problem.html", courses=get_courses(show), assignments=get_assignments(course, show), problems=problems, course_basics=get_course_basics(course), assignment_basics=get_assignment_basics(course, assignment), problem_basics=get_problem_basics(course, assignment, problem), problem_details=get_problem_details(course, assignment, problem, format_content=True, format_expected_output=True), next_prev_problems=get_next_prev_problems(course, assignment, problem, problems))
        except Exception as inst:
            render_error(self, traceback.format_exc())

class EditProblemHandler(RequestHandler):
    def get(self, course, assignment, problem):
        try:
            problems = get_problems(course, assignment)
            self.render("edit_problem.html", courses=get_courses(), assignments=get_assignments(course), problems=problems, course_basics=get_course_basics(course), assignment_basics=get_assignment_basics(course, assignment), problem_basics=get_problem_basics(course, assignment, problem), problem_details=get_problem_details(course, assignment, problem, format_expected_output=True, parse_data_urls=True), next_prev_problems=get_next_prev_problems(course, assignment, problem, problems), environments=sort_nicely(env_dict.keys()), result=None)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course, assignment, problem):
        try:
            #submitted_password = self.get_body_argument("password")
            submitted_password = password

            problem_basics = get_problem_basics(course, assignment, problem)
            problem_basics["title"] = self.get_body_argument("title").strip() #required
            problem_basics["visible"] = self.get_body_argument("is_visible") == "Yes" #required
            problem_details = {}
            problem_details["instructions"] = self.get_body_argument("instructions").strip().replace("\r", "") #required
            problem_details["environment"] = self.get_body_argument("environment")
            problem_details["output_type"] = self.get_body_argument("output_type")
            problem_details["answer_code"] = self.get_body_argument("answer_code").strip().replace("\r", "") #required
            problem_details["test_code"] = self.get_body_argument("test_code").strip().replace("\r", "")
            problem_details["credit"] = self.get_body_argument("credit").strip().replace("\r", "")
            problem_details["data_urls"] = self.get_body_argument("data_urls").strip().replace("\r", "")
            problem_details["show_expected"] = self.get_body_argument("show_expected") == "Yes"
            problem_details["show_test_code"] = self.get_body_argument("show_test_code") == "Yes"
            problem_details["expected_output"] = ""
            problem_details["data_urls_info"] = []

            result = "Error: Invalid password."

            if submitted_password == password:
                if problem_basics["title"] == "" or problem_details["instructions"] == "" or problem_details["answer_code"] == "":
                    result = "Error: One of the required fields is missing."
                else:
                    if has_duplicate_title(get_problems(course, assignment), problem, problem_basics["title"]):
                        result = "Error: A problem with that title already exists in this assignment."
                    else:
                        for data_url in set(problem_details["data_urls"].split("\n")):
                            data_url = data_url.strip()
                            if data_url != "":
                                contents, content_type = download_file(data_url)
                                md5_hash = create_md5_hash(data_url)
                                write_data_file(contents, md5_hash)
                                problem_details["data_urls_info"].append([data_url, md5_hash, content_type])

                        expected_output, error_occurred = exec_code(env_dict, problem_details["answer_code"], problem_basics, problem_details)

                        if error_occurred:
                            result = expected_output.decode()
                        else:
                            if problem_details["output_type"] == "txt":
                                problem_details["expected_output"] = expected_output.decode()
                            else:
                                problem_details["expected_output"] = expected_output

                            save_problem(problem_basics, problem_details)
                            problem_basics = get_problem_basics(course, assignment, problem)
                            problem_details = get_problem_details(course, assignment, problem, format_expected_output=True, parse_data_urls=True)
                            result = "Success: The problem was saved!"

            problems = get_problems(course, assignment)
            self.render("edit_problem.html", courses=get_courses(), assignments=get_assignments(course), problems=problems, course_basics=get_course_basics(course), assignment_basics=get_assignment_basics(course, assignment), problem_basics=problem_basics, problem_details=problem_details, next_prev_problems=get_next_prev_problems(course, assignment, problem, problems), environments=sort_nicely(env_dict.keys()), result=result)
        except Exception as inst:
            render_error(self, traceback.format_exc())

class DeleteProblemHandler(RequestHandler):
    def get(self, course, assignment, problem):
        try:
            problems = get_problems(course, assignment)
            self.render("delete_problem.html", courses=get_courses(), assignments=get_assignments(course), problems=problems, course_basics=get_course_basics(course), assignment_basics=get_assignment_basics(course, assignment), problem_basics=get_problem_basics(course, assignment, problem), next_prev_problems=get_next_prev_problems(course, assignment, problem, problems), result=None)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course, assignment, problem):
        try:
            #submitted_password = self.get_body_argument("password")
            submitted_password = password

            if submitted_password == password:
                delete_problem(get_problem_basics(course, assignment, problem))
                result = "Success: Problem deleted."
            else:
                result = "Error: Invalid password."

            problems = get_problems(course, assignment)
            self.render("delete_problem.html", courses=get_courses(), assignments=get_assignments(course), problems=problems, course_basics=get_course_basics(course), assignment_basics=get_assignment_basics(course, assignment), problem_basics=get_problem_basics(course, assignment, problem), next_prev_problems=get_next_prev_problems(course, assignment, problem, problems), result=result)
        except Exception as inst:
            render_error(self, traceback.format_exc())

class CheckProblemHandler(RequestHandler):
    async def post(self, course, assignment, problem):
        code = self.get_body_argument("code").replace("\r", "")

        problem_basics = get_problem_basics(course, assignment, problem)
        problem_details = get_problem_details(course, assignment, problem)
        out_dict = {"error_occurred": True, "passed": False, "diff_output": ""}

        try:
            if problem_details["output_type"] == "txt":
                code_output, error_occurred, passed, diff_output = test_code_txt(env_dict, code, problem_basics, problem_details, self.request)
            else:
                code_output, error_occurred, passed, diff_output = test_code_jpg(env_dict, code, problem_basics, problem_details, self.request)

            out_dict["code_output"] = format_output_as_html(code_output)
            out_dict["error_occurred"] = error_occurred
            out_dict["passed"] = passed
            out_dict["diff_output"] = diff_output
        except Exception as inst:
            out_dict["code_output"] = format_output_as_html(traceback.format_exc())

        self.write(json.dumps(out_dict))

class OutputTypesHandler(RequestHandler):
    def get(self, environment):
        try:
            self.write(" ".join(sort_nicely(env_dict[environment]["output_types"])))
        except Exception as inst:
            print(self, traceback.format_exc())
            self.write("\n".join(["txt"]))

class StaticFileHandler(RequestHandler):
    async def get(self, file_name):
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

class DataHandler(RequestHandler):
    async def get(self, course, assignment, problem, md5_hash):
        data_file_path = get_downloaded_file_path(md5_hash)

        problem_details = get_problem_details(course, assignment, problem)

        content_type = get_columns_dict(problem_details["data_urls_info"], 1, 2)[md5_hash]
        self.set_header('Content-type', content_type)

        if not os.path.exists(data_file_path) or is_old_file(data_file_path):
            url = get_columns_dict(problem_details["data_urls_info"], 1, 0)[md5_hash]

            ## Check to see whether the request came from the server or the user's computer
            #this_host = self.request.headers.get("Host")
            #referer = self.request.headers.get("Referer")
            #referer_url_parts = urllib.parse.urlparse(referer)
            #referer_host = referer_url_parts[1]
            #referer_path = referer_url_parts[2]

            #if referer_host == this_host and referer_path.startswith("/problem") and content_type.startswith("text/"):
            #    self.write("Please wait while the file is downloaded...\n\n")

            urllib.request.urlretrieve(url, data_file_path)

        self.write(read_file(data_file_path))

if __name__ == "__main__":
    if "PORT" in os.environ:
        application = make_app()

        #TODO: Store this securely or have a better way of authenticating.
        password = "abc"
        env_dict = get_environments()

        server = tornado.httpserver.HTTPServer(application)
        server.bind(int(os.environ['PORT']))
        server.start(int(os.environ['NUM_PROCESSES']))
        print("Starting on port {}...".format(os.environ['PORT']))
        tornado.ioloop.IOLoop.instance().start()
    else:
        print("No PORT environment variable was specified.")
        sys.exit(1)
