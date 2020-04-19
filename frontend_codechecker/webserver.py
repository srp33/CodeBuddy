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
        url(r"\/output_types\/([^\/]+)", OutputTypesHandler, name="output_types"),
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
            #submitted_password = self.get_body_argument("password")
            submitted_password = password

            courses = get_courses()
            course_basics = get_course_basics(course)
            course_basics["title"] = self.get_body_argument("title").strip()
            course_details = {"introduction": self.get_body_argument("introduction").strip()}

            if submitted_password == password:
                if course_basics["title"] == "" or course_details["introduction"] == "":
                    result = "Error: Missing title or introduction."
                else:
                    if has_duplicate_title(courses, course, course_basics["title"]):
                        result = "Error: A course with that title already exists."
                    else:
                        save_course(course_basics, course_details)
                        course_basics = get_course_basics(course)
                        courses = get_courses()
                        result = "Success: Course information saved!"
            else:
                result = "Error: Invalid password."

            self.render("edit_course.html", courses=courses, course_basics=course_basics, course_details=course_details, result=result)
        except Exception as inst:
            render_error(self, traceback.format_exc())

class AssignmentHandler(RequestHandler):
    def get(self, course, assignment):
        try:
            self.render("assignment.html", courses=get_courses(), course_basics=get_course_basics(course), assignment_basics=get_assignment_basics(course, assignment), assignment_details=get_assignment_details(course, assignment, True))
        except Exception as inst:
            render_error(self, traceback.format_exc())

class EditAssignmentHandler(RequestHandler):
    def get(self, course, assignment):
        try:
            self.render("edit_assignment.html", courses=get_courses(), course_basics=assignment_basics["course"], assignment_basics=get_assignment_basics(course, assignment), assignment_details=get_assignment_details(course, assignment), result=None)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course, assignment):
        try:
            #submitted_password = self.get_body_argument("password")
            submitted_password = password

            assignment_basics = get_assignment_basics(course, assignment)
            assignment_basics["title"] = self.get_body_argument("title").strip()
            assignment_details = {"introduction": self.get_body_argument("introduction").strip()}

            if submitted_password == password:
                if assignment_basics["title"] == "" or assignment_details["introduction"] == "":
                    result = "Error: Missing title or introduction."
                else:
                    if has_duplicate_title(assignment_basics["course"]["assignments"], assignment, assignment_basics["title"]):
                        result = "Error: An assignment with that title already exists."
                    else:
                        save_assignment(assignment_basics, assignment_details)
                        assignment_basics = get_assignment_basics(course, assignment)
                        result = "Success: Assignment information saved!"
            else:
                result = "Error: Invalid password."

            self.render("edit_assignment.html", courses=get_courses(), course_basics=get_course_basics(course), assignment_basics=assignment_basics, assignment_details=assignment_details, result=result)
        except Exception as inst:
            render_error(self, traceback.format_exc())

class ProblemHandler(RequestHandler):
    def get(self, course, assignment, problem):
        try:
            #course_exists, course_dict = get_course_info(course)
            #assignments = get_assignments(course, course_exists)
            #assignment_title = get_assignment_file(course, assignment, "assignment_title")
            #assignment_instructions = convert_markdown_to_html(get_problem_file(course, assignment, problem, "instructions"))
            #problem_title = get_problem_file(course, assignment, problem, "title")
            #output_type = get_problem_file(course, assignment, problem, "output_type")
            #show_expected = get_problem_file_bool(course, assignment, problem, "show_expected")
            #show_test_code = get_problem_file_bool(course, assignment, problem, "show_test_code")
            #credit = get_problem_file(course, assignment, problem, "credit")

            #data_urls_dict = {}
            #if os.path.exists(get_problem_file_path(course, assignment, problem, "data_urls")):
            #    data_urls_dict = get_problem_file_dict(course, assignment, problem, "data_urls", 0, 1)

            #problems = get_assignment_problems(course, assignment, course_exists, assignment_exists)
            #prev_problem = get_prev_problem(course, assignment, problem, problems)
            #next_problem = get_next_problem(course, assignment, problem, problems)

            #expected_output = ""
            #if show_expected:
            #    if output_type == "txt":
            #        expected_output = format_output_as_html(read_file(get_expected_path(course, assignment, problem)))
            #    else:
            #        expected_output = "/img/{}/{}/{}".format(course, assignment, problem)

            #test_code = ""
            #if show_test_code:
            #    test_code = format_output_as_html(get_problem_file(course, assignment, problem, "test_code"))

            self.render("problem.html", courses=get_courses(), course_basics=get_course_basics(course), assignment_basics=get_assignment_basics(course, assignment), problem_basics=get_problem_basics(course, assignment, problem), problem_details=get_problem_details(course, assignment, problem, True))
                    #this_course=course, this_course_title=course_dict["title"], this_assignment=assignment, this_assignment_title=assignment_title, instructions=assignment_instructions, data_urls_dict=data_urls_dict, assignments=assignments, this_problem=problem, this_problem_title=problem_title, problems=problems, output_type=output_type, test_code=test_code, expected_output=expected_output, prev_problem=prev_problem, next_problem=next_problem, credit=credit)
        except Exception as inst:
            render_error(self, traceback.format_exc())

class EditProblemHandler(RequestHandler):
    def get(self, course, assignment, problem):
        try:
            self.render("edit_problem.html", courses=get_courses(), course_basics=get_course_basics(course), assignment_basics=get_assignment_basics(course, assignment), problem_basics=get_problem_basics(course, assignment, problem), problem_details=get_problem_details(course, assignment, problem), environments=sort_nicely(env_dict.keys()), result=None)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course, assignment, problem):
        try:
            #submitted_password = self.get_body_argument("password")
            submitted_password = password

            problem_basics = get_problem_basics(course, assignment, problem)
            problem_basics["title"] = self.get_body_argument("title").strip() #required
            problem_details = {}
            problem_details["instructions"] = self.get_body_argument("instructions").strip() #required
            problem_details["environment"] = self.get_body_argument("environment")
            problem_details["output_type"] = self.get_body_argument("output_type")
            problem_details["answer_code"] = self.get_body_argument("answer_code").strip() #required
            problem_details["test_code"] = self.get_body_argument("test_code").strip()
            problem_details["credit"] = self.get_body_argument("credit").strip()
            problem_details["data_urls"] = self.get_body_argument("data_urls").strip()
            problem_details["show_expected"] = self.get_body_argument("show_expected") == "Yes"
            problem_details["show_test_code"] = self.get_body_argument("show_test_code") == "Yes"

            #environments = sort_nicely(env_dict.keys())
            #output_types = ["txt"]
            result = "Error: Invalid password."

            if submitted_password == password:
                if problem_basics["title"] == "" or problem_details["instructions"] == "" or problem_details["answer_code"] == "":
                    result = "Error: One of the required fields is missing."
                else:
                    problem_details["data_urls_info"] = []
                    for data_url in set(problem_details["data_urls"].split("\n")):
                        data_url = data_url.strip()
                        if data_url != "":
                            contents, content_type = download_file(data_url)
                            md5_hash = create_md5_hash(data_url)
                            write_data_file(contents, md5_hash)
                            problem_details["data_urls_info"].append([data_url, md5_hash, content_type])

                    expected_output, error_occurred = exec_code(env_dict, problem_details["answer_code"], problem_basics, problem_details, self.request)

                    if error_occurred:
                        result = "Error: {}".format(expected_output.decode())
                    else:
                        if problem_details["output_type"] == "txt":
                            problem_details["expected_output"] = expected_output.decode()
                        else:
                            problem_details["expected_output"] = encode_image_bytes(expected_output)

                        save_problem(problem_basics, problem_details)
                        problem_basics = get_problem_basics(course, assignment, problem)
                        result = "Success: The problem was saved!"

            self.render("edit_problem.html", courses=get_courses(), course_basics=get_course_basics(course), assignment_basics=get_assignment_basics(course, assignment), problem_basics=problem_basics, problem_details=problem_details, environments=sort_nicely(env_dict.keys()), result=result)
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

class OutputTypesHandler(RequestHandler):
    def get(self, environment):
        try:
            self.write(" ".join(sort_nicely(env_dict[environment]["output_types"])))
        except Exception as inst:
            print(self, traceback.format_exc())
            self.write("\n".join(["txt"]))

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
