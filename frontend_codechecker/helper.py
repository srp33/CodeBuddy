import base64
import difflib
import glob
import hashlib
import html
from imgcompare import *
import json
import os
from pathlib import Path
import re
import requests
from requests.exceptions import ReadTimeout
import shutil
import stat
import sys
import time
import yaml
from yaml import load
from yaml import Loader

timeout_seconds = 60

def rm_dir_recursively(dir_path):
    if os.path.exists(dir_path):
        for x in glob.glob("{}/*".format(dir_path)):
            if os.path.isdir(x):
                shutil.rmtree(x)
            else:
                os.remove(x)

def make_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def make_dir_for_file(file_path):
    make_dir(os.path.dirname(file_path))

def write_file(x, file_path, mode="w"):
    make_dir_for_file(file_path)

    with open(file_path, mode) as the_file:
        the_file.write(x)

def read_file(file_path, mode="r"):
    with open(file_path, mode) as the_file:
        return the_file.read()

def convert_markdown_to_html(text):
    html = text

    for match in re.findall(r"```[^`]+?```", html):
        #html = html.replace(match, "<code>" + match[3:-3].strip().replace("\n", "<br />") + "</code>")
        html = html.replace(match, "<pre>" + match[3:-3].strip() + "</pre>")

    html = re.sub(r"`(.+?)`", r"<code>\1</code>", html)
    html = html.replace("\n\n", "<p>")
#    html = re.sub(r"## ([^#.]+?)\n", r"<h2>\1</h2>\n", html)
#    html = re.sub(r"\* (.+?)", r"<li>\1", html)
#    html = re.sub(r"1\. (.+?)", r"<li>\1", html)
#    html = re.sub(r"\d+\. (.+?)", r"<li>\1", html)
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)
    html = re.sub(r"\[([^\[]+?)\]\((.+?)\)", r"<a href='\2'>\1</a>", html)

    #html = markdown.markdown(html)

#    for tag in ("p", "h1", "h2", "h3", "h4", "h5", "h6", "li"):
#        html = html.replace("<{}>".format(tag), "<{}{}>".format(tag, font))

    return html

def format_output_as_html(output):
    return html.escape(output).replace(" ", "&nbsp;").replace("\t", "&emsp;").replace("\n", "<br />")

# Kudos: https://arcpy.wordpress.com/2012/05/11/sorting-alphanumeric-strings-in-python/
def sorted_nicely(l):
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key = alphanum_key)

# From https://stackoverflow.com/questions/12485666/python-deleting-all-files-in-a-folder-older-than-x-days
#import arrow
#def remove_old_dirs(dir_path):
#    criticalTime = arrow.now().shift(minutes=-30)
#
#    for item in Path(dir_path).glob('*'):
#        itemTime = arrow.get(item.stat().st_mtime)
#        if itemTime < criticalTime:
#            shutil.rmtree(item)

def is_old_file(file_path, days):
    age_in_seconds = time.time() - os.stat(file_path)[stat.ST_MTIME]
    age_in_years = age_in_seconds / 60 / 60 / 24

    return age_in_years > days

def is_valid_password(handler):
    if handler.get_body_argument("password") != "larry_bird33":
        handler.write("You are an intruder!")
        return False
    return True

def get_courses():
    course_ids = sorted_nicely([os.path.basename(x) for x in glob.glob("/course/*")])

    courses = []
    for course_id in course_ids:
        exists, course_dict = get_course_info(course_id)
        courses.append((course_id, course_dict["title"], course_dict["introduction"]))

    return courses

def get_course_info(course_id, default_title=""):
    yaml_file_path = "{}/yaml".format(get_course_dir_path(course_id))

    yaml_dict = {}
    if os.path.exists(yaml_file_path):
        exists = True
        yaml_dict = load_yaml_dict(read_file(yaml_file_path))
    else:
        yaml_dict = {"title": default_title, "introduction": ""}
        exists = False

    return exists, yaml_dict

def get_course_dir_path(course_id):
    return "/course/{}/".format(course_id)

def get_course_file_path(course, file_name):
    return get_course_dir_path(course) + file_name

def get_course_file(course, file_name):
    file_path = get_course_file_path(course, file_name)
    return read_file(file_path)

def get_assignments(course):
    assignments = []
    for assignment_dir_path in sorted_nicely(glob.glob(get_course_dir_path(course) + "*")):
        if os.path.isdir(assignment_dir_path):
            assignment = os.path.basename(assignment_dir_path)
            exists, assignment_dict = get_assignment_info(course, assignment)
            if exists:
                assignments.append((assignment, assignment_dict["title"]))

    #assignments.reverse()
    return assignments

def get_assignment_info(course, assignment, default_title=""):
    yaml_file_path = "{}/yaml".format(get_assignment_dir_path(course, assignment))

    if assignment == "" or not os.path.exists(yaml_file_path):
        return False, {"title": default_title, "introduction": ""}
    else:
        return True, load_yaml_dict(read_file(yaml_file_path))

#def check_assignment_exists(assignment, assignments):
#    return len([x for x in assignments if x[0] == assignment]) > 0

def get_assignment_dir_path(course, assignment):
    return "/course/{}/{}".format(course, assignment)

def get_assignment_file_path(course, assignment, file_name):
    return "{}/{}".format(get_assignment_dir_path(course, assignment), file_name)

def get_assignment_file(course, assignment, file_name):
    return read_file(get_assignment_file_path(course, assignment, file_name))

def get_assignment_problems(course, assignment):
    problems = []
    for problem_num in sorted_nicely([os.path.basename(x) for x in glob.glob("/course/{}/{}/test/*".format(course, assignment))]):
        problem_title = get_problem_file(course, assignment, problem_num, "title")
        problems.append((problem_num, problem_title))

    return problems

def get_problem_file_path(course, assignment, problem, file_id):
    return "/course/{}/{}/{}/{}".format(course, assignment, file_id, problem)

def get_problem_file(course, assignment, problem, file_id):
    return read_file(get_problem_file_path(course, assignment, problem, file_id)).strip()

def get_problem_file_bool(course, assignment, problem, file_id):
    return get_problem_file(course, assignment, problem, file_id).lower() == "true"

#def get_problem_file_list(course, assignment, problem, file_id):
#    my_list = []
#
#    file_contents = get_problem_file(course, assignment, problem, file_id)
#    if len(file_contents) > 0:
#        my_list = [line for line in file_contents.split("\n") if len(line.rstrip("\n")) > 0]
#
#    return my_list

def get_problem_file_dict(course, assignment, problem, file_id, key_col_index, value_col_index):
    my_dict = {}

    file_contents = get_problem_file(course, assignment, problem, file_id)
    if len(file_contents) > 0:
        for line in file_contents.split("\n"):
            line_items = line.split("\t")
            key = line_items[key_col_index]
            value = line_items[value_col_index]
            my_dict[key] = value

    return my_dict

def get_expected_path(course, assignment, problem):
    return "{}/expected/{}".format(get_assignment_dir_path(course, assignment), problem)

def get_prev_problem(course, assignment, problem, assignment_problems):
    if problem == assignment_problems[0][0]:
        return None

    return assignment_problems[int(problem) - 2][0]

def get_next_problem(course, assignment, problem, assignment_problems):
    if problem == assignment_problems[-1][0]:
        return None

    return assignment_problems[int(problem)][0]

def get_answer_file_name(problem, output_type):
    return problem.replace(get_file_extension(problem), "." + output_type)

def exec_code(settings_dict, code, test_code, output_type, course, assignment, problem, request):
    try:
        code = code + "\n\n" + test_code

        if os.path.exists(get_problem_file_path(course, assignment, problem, "data_urls")):
            for url, md5_hash in get_problem_file_dict(course, assignment, problem, "data_urls", 0, 1).items():
                cache_url = "{}://{}/data/{}/{}/{}/{}".format(
                        request.protocol,
                        request.host,
                        course, assignment, problem, md5_hash)
                code = code.replace(url, cache_url)

        timeout = settings_dict["timeout_seconds"] + 2
        data_dict = {"code": code, "timeout_seconds": timeout, "output_type": output_type}

        response = requests.post(settings_dict["url"], json.dumps(data_dict), timeout=timeout)
        return response.content, response.status_code != 200
    except ReadTimeout as inst:
        return "Your code did not finish executing before the time limit: {} seconds.".format(timeout).encode(), True

def test_code_txt(settings_dict, course, assignment, problem, code, test_code, show_expected, request):
    code_output, error_occurred = exec_code(settings_dict, code, test_code, "txt", course, assignment, problem, request)
    code_output = code_output.decode()

    if error_occurred:
        return code_output, True, False, ""

    expected_output = read_file(get_expected_path(course, assignment, problem))
    passed = expected_output == code_output

    diff_output = ""
    if not passed and show_expected:
        diff_output = diff_strings(expected_output, code_output)

    return code_output, error_occurred, passed, diff_output

def test_code_jpg(settings_dict, course, assignment, problem, code, test_code, show_expected, request):
    code_output, error_occurred = exec_code(settings_dict, code, test_code, "jpg", course, assignment, problem, request)

    if error_occurred:
        return code_output.decode(), True, False, ""

    expected_bytes = read_file(get_expected_path(course, assignment, problem), "rb")
    passed, diff_image = are_images_similar(expected_bytes, code_output)

    diff_output = ""
    if not passed and show_expected:
        diff_output = encode_image_bytes(convert_image_to_bytes(diff_image))

    code_output = encode_image_bytes(code_output)

    return code_output, error_occurred, passed, diff_output

def encode_image_bytes(b):
    return str(base64.b64encode(b), "utf-8")

def convert_dict_to_yaml(the_dict):
    return yaml.dump(the_dict)

def load_yaml_dict(yaml_text):
    return load(yaml_text, Loader=Loader)

def get_env_yaml():
    return load_yaml_dict(read_file("/Environments.yaml"))

def diff_strings(expected, actual):
    expected = expected.rstrip()
    actual = actual.rstrip()

    diff = difflib.ndiff(expected, actual)

    diff_output = ""
    #numChars = 0
    #numDifferences = 0

    for x in diff:
        sign = x[0]
        character = x[2]

        #numChars += 1

        if sign == " ":
            diff_output += character
        else:
            #numDifferences += 1

            #if character == "\n" or character == "\t" or character == " ":
            #    hasWhitespaceDiff = True

            if character == "\n":
                diff_output += "[\\n{}]\n".format(sign)
            else:
                diff_output += "[{}{}]".format(character, sign)

    # Only return diff output if the differences are relatively small.
    #if numDifferences / numChars > 0.2:
    #    diff_output = "More than 20% of the characters were different."

    return diff_output

def render_error(handler, exception):
    handler.render("error.html", error_title="An internal error occurred", error_message=format_output_as_html(exception))

def create_md5_hash(my_string):
    return hashlib.md5(my_string.encode("utf-8")).hexdigest()

def download_file(url):
    response = requests.get(url)
    if 'Content-type' in response.headers:
        content_type = response.headers['Content-type']
    else:
        content_type = "text/plain"

    return response.content, content_type
