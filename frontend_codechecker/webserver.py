from helper import *
import json
import re
import tornado.ioloop
from tornado.web import *
import traceback
import urllib.request
import uuid

error_title = "An error occurred."
#TODO: Store this securely or have a better way of authenticating.
password = "abc"
env_dict = get_env_yaml()

def make_app():
    return Application([
        url(r"/", HomeHandler),
        url(r"\/course\/([^\/]+)", CourseHandler, name="course"),
        url(r"\/edit_course\/([^\/]+)", EditCourseHandler, name="edit_course"),
        url(r"\/assignment\/([^\/]+)\/([^\/]+)", AssignmentHandler, name="assignment"),
        url(r"\/edit_assignment\/([^\/]+)\/([^\/]+)", EditAssignmentHandler, name="edit_assignment"),
        url(r"\/problem\/([^\/]+)\/([^\/]+)/([^\/]+)", ProblemHandler, name="problem"),
        url(r"\/check_problem\/([^\/]+)\/([^\/]+)/([^\/]+)", CheckProblemHandler, name="check_problem"),
        url(r"/img\/([^\/]+)\/([^\/]+)/([^\/]+)", ImageHandler, name="img"),
        url(r"/css/([^\/]+)", CssHandler, name="css"),
        url(r"/js/([^\/]+)", JavascriptHandler, name="javascript"),
        url(r"/data/([^\/]+)\/([^\/]+)/([^\/]+)/([^\/]+)", DataHandler, name="data"),
    ], autoescape=None)

class HomeHandler(RequestHandler):
    async def get(self):
        try:
            self.render("home.html", courses=get_courses())
        except Exception as inst:
            render_error(self, traceback.format_exc())

class CourseHandler(RequestHandler):
    async def get(self, course):
        try:
            courses = get_courses()
            course_exists, course_title, course_introduction = get_course_info(courses, course)

            self.render("course.html", courses=courses, this_course=course, this_course_title=course_title, introduction=course_introduction, assignments=get_assignments(course))
        except Exception as inst:
            render_error(self, traceback.format_exc())

class EditCourseHandler(RequestHandler):
    async def get(self, course):
        try:
            courses = get_courses()
            course_exists, course_title, course_introduction = get_course_info(courses, course)

            yaml_content = ""
            if course_exists:
                yaml_content = get_course_file(course, "yaml_content")

            self.render("edit_course.html", courses=courses, this_course=course, course_exists=course_exists, this_course_title=course_title, introduction=course_introduction, yaml_content=yaml_content)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def post(self, course):
        try:
            # This is a temporary solution
            if self.get_body_argument("password") != password:
                self.write(json.dumps({"error": "Invalid password"}))
                return

            yaml_content = self.get_body_argument("yaml_content")
            yaml_dict = load_yaml_dict(yaml_content)

            write_file(yaml_dict["title"], get_course_file_path(course, "title"))
            introduction = convert_markdown_to_html(yaml_dict["introduction"])
            write_file(introduction, get_course_file_path(course, "introduction"))
            write_file(yaml_content, get_course_file_path(course, "yaml_content"))

            self.write(json.dumps({"title": yaml_dict["title"], "introduction": introduction, "error": ""}))
        except Exception as inst:
            self.write(json.dumps({"error": format_output_as_html(traceback.format_exc())}))

class AssignmentHandler(RequestHandler):
    async def get(self, course, assignment):
        try:
            courses = get_courses()
            course_exists, course_title, course_introduction = get_course_info(courses, course)
            assignments = get_assignments(course)

            assignment_title = "This assignment has not been created."
            introduction = "Not yet specified."
            problems = []

            if course_exists and check_assignment_exists(assignment, assignments):
                assignment_title = get_assignment_file(course, assignment, "assignment_title")
                introduction = get_assignment_file(course, assignment, "introduction")
                problems = get_assignment_problems(course, assignment)

            self.render("assignment.html", introduction=introduction, courses=courses, this_course=course, this_course_title=course_title, assignments=assignments, this_assignment=assignment, this_assignment_title=assignment_title, problems=problems)
        except Exception as inst:
            render_error(self, traceback.format_exc())

class EditAssignmentHandler(RequestHandler):
    async def get(self, course, assignment):
        try:
            courses = get_courses()
            course_exists, course_title, course_introduction = get_course_info(courses, course)

            assignments = get_assignments(course)
            assignment_exists = check_assignment_exists(assignment, assignments)

            assignment_title = "Not yet specified"
            introduction = "Not yet specified"
            yaml_content = ""
            if course_exists and assignment_exists:
                assignment_title = get_assignment_file(course, assignment, "assignment_title")
                introduction = get_assignment_file(course, assignment, "introduction")
                yaml_content = get_assignment_file(course, assignment, "yaml_content")

            self.render("edit_assignment.html", courses=get_courses(), this_course=course, course_exists=course_exists, this_course_title=course_title, assignments=assignments, this_assignment=assignment, assignment_exists=assignment_exists, this_assignment_title=assignment_title, introduction=introduction, yaml_content=yaml_content)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def post(self, course, assignment):
        try:
            # This is a temporary solution
            if self.get_body_argument("password") != password:
                self.write(json.dumps({"error": "Invalid password"}))
                return

            yaml_content = self.get_body_argument("yaml_content")
            yaml_dict = load_yaml_dict(yaml_content)

            assignment_title = convert_markdown_to_html(yaml_dict["title"])
            introduction = convert_markdown_to_html(yaml_dict["introduction"])

            assignment_dir_path = get_assignment_dir_path(course, assignment)
            if os.path.exists(assignment_dir_path):
                for x in glob.glob("{}/*".format(assignment_dir_path)):
                    if os.path.isdir(x):
                        shutil.rmtree(x)
                    else:
                        os.remove(x)

            all_expected_output = ""
            problem_number = 0
            error = ""
            for problem_dict in yaml_dict["problems"]:
                problem_number += 1
                if "title" not in problem_dict:
                    problem_dict["test"] = "No title"
                if "test" not in problem_dict:
                    problem_dict["test"] = ""
                if "show_expected" not in problem_dict:
                    problem_dict["show_expected"] = True
                if "show_tests" not in problem_dict:
                    problem_dict["show_tests"] = True

                if "data_urls" in problem_dict:
                    data_url_output = ""
                    for data_url in set(problem_dict["data_urls"]):
                        contents, content_type = download_file(data_url)
                        data_url_output += "{}\t{}\t{}\n".format(data_url, create_md5_hash(data_url), content_type)

                    write_file(data_url_output, "{}/data_urls/{}".format(assignment_dir_path, problem_number))

                expected_output, error_occurred = exec_code(env_dict[problem_dict["environment"]], problem_dict["answer"], problem_dict["test"], problem_dict["output_type"], course, assignment, problem_number, self.request)

                if error_occurred:
                    error = expected_output.decode()

                all_expected_output += str(problem_number) + ":\n"
                if problem_dict["output_type"] == "txt":
                    all_expected_output += "<p><pre>" + expected_output.decode() + "</pre></p>\n"
                else:
                    all_expected_output += "<p><figure class='img'><img src='data:image/jpg;base64," + encode_image_bytes(expected_output) + "' width='95%' /></figure></p>\n"

                write_file(expected_output, "{}/expected/{}".format(assignment_dir_path, str(problem_number)), "wb")
                for x in ("title", "instructions", "environment", "output_type", "test", "show_expected", "show_tests"):
                    write_file(str(problem_dict[x]), "{}/{}/{}".format(assignment_dir_path, x, str(problem_number)))

                all_expected_output += "\n"

            write_file(yaml_content, get_assignment_file_path(course, assignment, "yaml_content"))
            write_file(assignment_title, get_assignment_file_path(course, assignment, "assignment_title"))
            write_file(introduction, get_assignment_file_path(course, assignment, "introduction"))

            self.write(json.dumps({"title": assignment_title, "introduction": introduction, "expected_output": all_expected_output, "error": error}))
        except Exception as inst:
            self.write(json.dumps({"error": format_output_as_html(traceback.format_exc())}))

class ProblemHandler(RequestHandler):
    async def get(self, course, assignment, problem):
        try:
            courses = get_courses()
            course_exists, course_title, course_introduction = get_course_info(courses, course)
            assignments = get_assignments(course)
            assignment_title = get_assignment_file(course, assignment, "assignment_title")
            assignment_instructions = convert_markdown_to_html(get_problem_file(course, assignment, problem, "instructions"))
            problem_title = get_problem_file(course, assignment, problem, "title")
            output_type = get_problem_file(course, assignment, problem, "output_type")
            show_expected = get_problem_file_bool(course, assignment, problem, "show_expected")
            show_tests = get_problem_file_bool(course, assignment, problem, "show_tests")

            data_urls_dict = {}
            if os.path.exists(get_problem_file_path(course, assignment, problem, "data_urls")):
                data_urls_dict = get_problem_file_dict(course, assignment, problem, "data_urls", 0, 1)

            problems = get_assignment_problems(course, assignment)
            prev_problem = get_prev_problem(course, assignment, problem, problems)
            next_problem = get_next_problem(course, assignment, problem, problems)

            expected_output = ""
            if show_expected:
                if output_type == "txt":
                    expected_output = format_output_as_html(read_file(get_expected_path(course, assignment, problem)))
                else:
                    expected_output = "/img/{}/{}/{}".format(course, assignment, problem)

            test_code = ""
            if show_tests:
                test_code = format_output_as_html(get_problem_file(course, assignment, problem, "test"))

            self.render("problem.html", courses=courses, this_course=course, this_course_title=course_title, this_assignment=assignment, this_assignment_title=assignment_title, instructions=assignment_instructions, data_urls_dict=data_urls_dict, assignments=assignments, this_problem=problem, this_problem_title=problem_title, problems=problems, output_type=output_type, test_code=test_code, expected_output=expected_output, prev_problem=prev_problem, next_problem=next_problem)
        except Exception as inst:
            render_error(self, traceback.format_exc())

class CheckProblemHandler(RequestHandler):
    async def post(self, course, assignment, problem):
        code = self.get_body_argument("code")
        environment = get_problem_file(course, assignment, problem, "environment")
        test_code = get_problem_file(course, assignment, problem, "test")
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
        data_file_path = "/data/{}".format(md5_hash)

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

        server = tornado.httpserver.HTTPServer(application)
        server.bind(int(os.environ['PORT']))
        server.start(int(os.environ['NUM_PROCESSES']))
        print("Starting on port {}...".format(os.environ['PORT']))
        tornado.ioloop.IOLoop.instance().start()
    else:
        print("No PORT environment variable was specified.")
        sys.exit(1)
