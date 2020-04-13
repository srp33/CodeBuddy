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
        url(r"\/assignment\/([^\/]+)\/([^\/]+)", AssignmentHandler, name="assignment"),
        url(r"\/edit_assignment\/([^\/]+)\/([^\/]+)?", EditAssignmentHandler, name="edit_assignment"),
        url(r"\/problem\/([^\/]+)\/([^\/]+)/([^\/]+)", ProblemHandler, name="problem"),
        url(r"\/edit_problem\/([^\/]+)\/([^\/]+)/([^\/]+)?", EditProblemHandler, name="edit_problem"),
        url(r"\/check_problem\/([^\/]+)\/([^\/]+)/([^\/]+)", CheckProblemHandler, name="check_problem"),
        url(r"/img\/([^\/]+)\/([^\/]+)/([^\/]+)", ImageHandler, name="img"),
        url(r"/css/([^\/]+)", CssHandler, name="css"),
        url(r"/js/([^\/]+)", JavascriptHandler, name="javascript"),
        url(r"/data/([^\/]+)\/([^\/]+)/([^\/]+)/([^\/]+)", DataHandler, name="data"),
    ], autoescape=None)

class HomeHandler(RequestHandler):
    def get(self):
        try:
            self.render("home.html", courses=get_courses())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class CourseHandler(RequestHandler):
    def get(self, course):
        try:
            self.render("course.html", courses=get_courses(), course_basics=get_course_basics(course), course_details=get_course_details(course, True))
        except Exception as inst:
            render_error(self, traceback.format_exc())

class EditCourseHandler(RequestHandler):
    def get(self, course):
        try:
            self.render("edit_course.html", courses=get_courses(), course_basics=get_course_basics(course), course_details=get_course_details(course), result=None)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course):
        try:
            submitted_password = self.get_body_argument("password")
            title = self.get_body_argument("title").strip()
            introduction = self.get_body_argument("introduction").strip()

            courses = get_courses()
            course_basics = get_course_basics(course)
            course_basics["title"] = title
            course_details = {"introduction": introduction}

            if submitted_password == password:
                if title == "" or introduction == "":
                    result = "Error: Missing title or introduction."
                else:
                    if has_duplicate_title(courses, course, title):
                        result = "Error: A course with that title already exists."
                    else:
                        save_course(course_basics, course_details)
                        course_basics["exists"] = True
                        result = "Success: Course information saved!"
            else:
                result = "Error: Invalid password."

            self.render("edit_course.html", courses=courses, course_basics=course_basics, course_details=course_details, result=result)
        except Exception as inst:
            render_error(self, traceback.format_exc())

class AssignmentHandler(RequestHandler):
    def get(self, course, assignment):
        try:
            course_exists, course_dict = get_course_info(course)
            assignment_exists, assignment_dict = get_assignment_info(course, assignment)

            self.render("assignment.html", introduction=convert_markdown_to_html(assignment_dict["introduction"]), courses=get_courses(), course_exists=course_exists, this_course=course, this_course_title=convert_markdown_to_html(course_dict["title"]), assignments=get_assignments(course, course_exists), assignment_exists=assignment_exists, this_assignment=assignment, this_assignment_title=convert_markdown_to_html(assignment_dict["title"]), problems=get_assignment_problems(course, assignment, course_exists, assignment_exists), new_problem_id=create_id())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class EditAssignmentHandler(RequestHandler):
    def get(self, course, assignment):
        try:
            course_exists, course_dict = get_course_info(course)

            if course_exists:
                assignment_exists, assignment_dict = get_assignment_info(course, assignment)
                result = None
            else:
                result = f"A course with this identifier [{course}] does not exist."
                assignment_exists = get_default_assignment_info()

            self.render("edit_assignment.html", courses=get_courses(), this_course=course, course_exists=course_exists, this_course_title=course_dict["title"], assignments=get_assignments(course, course_exists), this_assignment=assignment, assignment_exists=assignment_exists, this_assignment_title=assignment_dict["title"], this_assignment_introduction=assignment_dict["introduction"], result=result)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course_id, assignment_id):
        try:
            submitted_password = self.get_body_argument("password")
            title = self.get_body_argument("assignment_title").strip()
            introduction = self.get_body_argument("assignment_introduction").strip()
            result = ""
            course_exists, course_dict = get_course_info(course_id)
            assignments = get_assignments(course_id, course_exists)

            if submitted_password == password:
                if not course_exists:
                    result = "Error: Invalid course identifier."
                else:
                    if title == "" or introduction == "":
                        result = "Error: Missing title or introduction."
                    else:
                        # Make sure we don't have an assignment with a duplicate title
                        duplicate = False
                        for assignment in assignments:
                            if assignment[0] != assignment_id and assignment[1] == title:
                                duplicate = True
                                break
                        if duplicate:
                            result = "Error: An assignment with that title already exists."
                        else:
                            assignment_dict = {"id": assignment_id, "title": title, "introduction": introduction}
                            write_file(convert_dict_to_yaml(assignment_dict), get_assignment_file_path(course_id, assignment_id, "yaml"))

                            result = "Success: Assignment information saved!"
            else:
                result = "Error: Invalid password."

            self.render("edit_assignment.html", courses=get_courses(), this_course=course_id, course_exists=course_exists, this_course_title=course_dict["title"], assignments=assignments, this_assignment=assignment_id, assignment_exists=True, this_assignment_title=title, this_assignment_introduction=introduction, result=result)
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ProblemHandler(RequestHandler):
    def get(self, course, assignment, problem):
        try:
            course_exists, course_dict = get_course_info(course)
            assignments = get_assignments(course, course_exists)
            assignment_title = get_assignment_file(course, assignment, "assignment_title")
            assignment_instructions = convert_markdown_to_html(get_problem_file(course, assignment, problem, "instructions"))
            problem_title = get_problem_file(course, assignment, problem, "title")
            output_type = get_problem_file(course, assignment, problem, "output_type")
            show_expected = get_problem_file_bool(course, assignment, problem, "show_expected")
            show_test_code = get_problem_file_bool(course, assignment, problem, "show_test_code")
            credit = get_problem_file(course, assignment, problem, "credit")

            data_urls_dict = {}
            if os.path.exists(get_problem_file_path(course, assignment, problem, "data_urls")):
                data_urls_dict = get_problem_file_dict(course, assignment, problem, "data_urls", 0, 1)

            problems = get_assignment_problems(course, assignment, course_exists, assignment_exists)
            prev_problem = get_prev_problem(course, assignment, problem, problems)
            next_problem = get_next_problem(course, assignment, problem, problems)

            expected_output = ""
            if show_expected:
                if output_type == "txt":
                    expected_output = format_output_as_html(read_file(get_expected_path(course, assignment, problem)))
                else:
                    expected_output = "/img/{}/{}/{}".format(course, assignment, problem)

            test_code = ""
            if show_test_code:
                test_code = format_output_as_html(get_problem_file(course, assignment, problem, "test_code"))

            self.render("problem.html", courses=get_courses(), this_course=course, this_course_title=course_dict["title"], this_assignment=assignment, this_assignment_title=assignment_title, instructions=assignment_instructions, data_urls_dict=data_urls_dict, assignments=assignments, this_problem=problem, this_problem_title=problem_title, problems=problems, output_type=output_type, test_code=test_code, expected_output=expected_output, prev_problem=prev_problem, next_problem=next_problem, credit=credit)
        except Exception as inst:
            render_error(self, traceback.format_exc())

class EditProblemHandler(RequestHandler):
    def get(self, course, assignment, problem):
        try:
            problem_exists = False
            problems = []
            environments = sort_nicely(env_dict.keys())
            output_types = ["txt"]
            course_exists, course_dict = get_course_info(course)

            if course_exists:
                assignment_exists, assignment_dict = get_assignment_info(course, assignment)

                if assignment_exists:
                    problem_exists, problem_dict = get_problem_info(course, assignment, problem)
                    problems = get_assignment_problems(course, assignment, course_exists, assignment_exists)
                    result = None
                else:
                    result = f"An assignment with this identifier [{assignment}] does not exist."
            else:
                result = f"A course with this identifier [{course}] does not exist."

            self.render("edit_problem.html", courses=get_courses(), this_course=course, course_exists=course_exists, this_course_title=course_dict["title"], assignments=get_assignments(course, course_exists), this_assignment=assignment, assignment_exists=assignment_exists, this_assignment_title=assignment_dict["title"], this_assignment_introduction=assignment_dict["introduction"], this_problem=problem, problem_exists=problem_exists, this_problem_title=problem_dict["title"], problem_dict=problem_dict, problems=problems, prev_problem=None, next_problem=None, environments=environments, output_types=output_types, result=result)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course, assignment, problem):
        try:
            submitted_password = self.get_body_argument("password")
            problem_dict = {}
            problem_dict["title"] = self.get_body_argument("title").strip() #required
            problem_dict["instructions"] = self.get_body_argument("instructions").strip() #required
            problem_dict["environment"] = self.get_body_argument("environment")
            problem_dict["output_type"] = self.get_body_argument("output_type")
            problem_dict["answer_code"] = self.get_body_argument("answer_code").strip() #required
            problem_dict["test_code"] = self.get_body_argument("test_code").strip()
            problem_dict["credit"] = self.get_body_argument("credit").strip()
            problem_dict["data_urls"] = self.get_body_argument("data_urls").strip()
            problem_dict["show_expected"] = self.get_body_argument("show_expected") == "Yes"
            problem_dict["show_test_code"] = self.get_body_argument("show_test_code") == "Yes"

            course_exists, course_dict = get_course_info(course)
            assignment_exists, assignment_dict = get_assignment_info(course, assignment)
            problems = []
            environments = sort_nicely(env_dict.keys())
            output_types = ["txt"]
            result = "Error: Invalid password."

            if submitted_password == password:
                if not course_exists or not assignment_exists:
                    result = "Error: Invalid course identifier or invalid assignment identifier."
                else:
                    if problem_dict["title"] == "" or problem_dict["instructions"] == "" or problem_dict["answer_code"] == "":
                        result = "Error: One of the required fields is missing."
                    else:
                        problems = get_assignment_problems(course, assignment, True, True)

                        problem_dict["data_urls_info"] = []
                        for data_url in set(problem_dict["data_urls"].split("\n")):
                            data_url = data_url.strip()
                            if data_url != "":
                                contents, content_type = download_file(data_url)
                                md5_hash = create_md5_hash(data_url)
                                write_data_file(contents, md5_hash)
                                problem_dict["data_urls_info"].append([data_url, md5_hash, content_type])

                        expected_output, error_occurred = exec_code(env_dict[problem_dict["environment"]], problem_dict["answer_code"], problem_dict["test_code"], problem_dict["output_type"], course, assignment, problem, self.request)

                        if error_occurred:
                            result = "Error: {}".format(expected_output.decode())
                        else:
                            if problem_dict["output_type"] == "txt":
                                problem_dict["expected_output"] = expected_output.decode()
                            else:
                                problem_dict["expected_output"] = encode_image_bytes(expected_output)

                            write_file(convert_dict_to_yaml(problem_dict), get_problem_file_path(course, assignment, problem, "yaml"))
                            result = "Success: The problem was saved!"

            self.render("edit_problem.html", courses=get_courses(), this_course=course, course_exists=course_exists, this_course_title=course_dict["title"], assignments=get_assignments(course, course_exists), this_assignment=assignment, assignment_exists=assignment_exists, this_assignment_title=assignment_dict["title"], this_assignment_introduction=assignment_dict["introduction"], this_problem=problem, problem_exists=True, this_problem_title=problem_dict["title"], problem_dict=problem_dict, problems=problems, prev_problem=None, next_problem=None, environments=environments, output_types=output_types, result=result)
        except Exception as inst:
            render_error(self, traceback.format_exc())

class CheckProblemHandler(RequestHandler):
    async def post(self, course, assignment, problem):
        code = self.get_body_argument("code")
        environment = get_problem_file(course, assignment, problem, "environment")
        test_code = get_problem_file(course, assignment, problem, "test_code")
        output_type = get_problem_file(course, assignment, problem, "output_type")
        show_expected = get_problem_file_bool(course, assignment, problem, "show_expected")
        out_dict = {"error_occurred": True, "passed": False, "diff_output": ""}

        try:
            if output_type == "txt":
                code_output, error_occurred, passed, diff_output = test_code_txt(env_dict[environment], course, assignment, problem, code, test_code, show_expected, self.request)
            else:
                code_output, error_occurred, passed, diff_output = test_code_jpg(env_dict[environment], course, assignment, problem, code, test_code, show_expected, self.request)

            out_dict["code_output"] = format_output_as_html(code_output)
            out_dict["error_occurred"] = error_occurred
            out_dict["passed"] = passed
            out_dict["diff_output"] = diff_output
        except Exception as inst:
            out_dict["code_output"] = format_output_as_html(traceback.format_exc())

        self.write(json.dumps(out_dict))

class ImageHandler(RequestHandler):
    async def get(self, course, assignment, problem):
        image_bytes = read_file(get_expected_path(course, assignment, problem), mode="rb")

        self.set_header('Content-type', 'image/jpg')
        self.set_header('Content-length', len(image_bytes))
        self.write(image_bytes)

class CssHandler(RequestHandler):
    async def get(self, filename):
        file_path = "/static/{}".format(filename)
        file_contents = read_file(file_path)

        self.set_header('Content-type', 'text/css')
        self.write(file_contents)

class JavascriptHandler(RequestHandler):
    async def get(self, filename):
        file_path = "/static/{}".format(filename)
        file_contents = read_file(file_path)

        self.set_header('Content-type', 'text/javascript')
        self.write(file_contents)

class DataHandler(RequestHandler):
    async def get(self, course, assignment, problem, md5_hash):
        data_file_path = get_downloaded_file_path(md5_hash)

        content_type = get_problem_file_dict(course, assignment, problem, "data_urls", 1, 2)[md5_hash]
        self.set_header('Content-type', content_type)

        if not os.path.exists(data_file_path) or is_old_file(data_file_path, days=7):
            url = get_problem_file_dict(course, assignment, problem, "data_urls", 1, 0)[md5_hash]

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
