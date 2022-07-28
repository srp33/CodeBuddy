import base64
from datetime import datetime
import difflib
import glob
import hashlib
import html
from imgcompare import *
import json
from markdown2 import Markdown
import os
from pathlib import Path
import random
import re
import requests
from requests.exceptions import *
import shutil
import stat
import string
import subprocess
import sys
import time
from tornado.web import RequestHandler
import uuid
import yaml
from yaml import load
from yaml import Loader

def run_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return "".join(result.stdout.decode().split("\n"))

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

def is_old_file(file_path, days=30):
    age_in_seconds = time.time() - os.stat(file_path)[stat.ST_MTIME]
    age_in_days = age_in_seconds / 60 / 60 / 24
    return age_in_days > days

def convert_html_to_markdown(text):
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace('&nbsp;', '')
    text = re.sub(r"<(/*)span(.*?)>", "", text) # Removes opening and closing <span> tags.
    text = re.sub(r"<(/*)br(.*?)>", "", text) # Removes <br> tags.
    text = re.sub(r"<(div|p)(.*?)>", "\n", text) # Replaces <div> and <p> tags with a newline.
    text = re.sub(r"<(/*)(div|p)(.*?)>", "", text) # Removes closing <div> and <p> tags.
    text = re.sub(r'<img src="([^">]+?)">', r"![](\1)", text) # Formats images for markdown.

    return text

def convert_markdown_to_html(text):
    if not text or len(text) == 0:
        return ""

    markdown = Markdown()

    html = re.sub(r"youtube:([-_a-zA-Z0-9]+)", r"<iframe width='800' height='550' src='https://www.youtube.com/embed/\1?controls=1'></iframe>\n", text)
    html = re.sub(r"panopto:([a-zA-Z0-9\.]+.panopto.com)\/([-_a-z0-9]+)", r"<p style='text-align: left;'>\n<iframe id='panopto_iframe' style='border: 1px solid #464646;' title='embedded content' src='https://\1/Panopto/Pages/Embed.aspx?id=\2&amp;autoplay=false&amp;offerviewer=true&amp;showtitle=false&amp;showbrand=false&amp;captions=false&amp;interactivity=none' width='100%' height='450' allowfullscreen='allowfullscreen' allow='autoplay'></iframe>\n</p>\n", html)
    html = re.sub(r'```(.+?)```', r"<code>\1</code>", html)  # Formats single line code chunks
    html = re.sub(r'```([\s\S]*?)```', r"<pre><code>\1</code></pre>", html) # Formats multiline code blocks
    html = re.sub(r'<pre><code>\n', r"<pre><code>", html) # Removes extra newline, if present
    html = markdown.convert(html)
    html = re.sub(r"<a href=\"([^\"]+)\">", r"<a href='\1' target='_blank' rel='noopener noreferrer'>", html)

    return html

# This function addresses a temporary problem and may be removed when it is no longer needed.
def remove_html_tags(text):
    #text = text.replace("<div><br></div>", "\n\n")
    text = text.replace("<div>", "\n")
    text = re.sub(r"<[^>]*>", "", text)

    return text

def format_output_as_html(output):
    return html.escape(output).replace(" ", "&nbsp;").replace("\t", "&emsp;").replace("\n", "<br />").replace("`", "&#96;")

# Kudos: https://arcpy.wordpress.com/2012/05/11/sorting-alphanumeric-strings-in-python/
def sort_nicely(l):
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key = alphanum_key)

def sort_list_of_dicts_nicely(lst, key):
    sort_dict = {}
    for item in lst:
        sort_dict[item[key]] = item

    sorted_list = []
    for dict_key in sort_nicely(sort_dict.keys()):
        sorted_list.append(sort_dict[dict_key])

    return sorted_list

def get_columns_dict(nested_list, key_col_index, value_col_index):
    columns_dict = {}
    for row in nested_list:
        columns_dict[row[key_col_index]] = row[value_col_index]
    return columns_dict

def exec_code(settings_dict, code, verification_code, exercise_details, add_formatted_txt = False):
    # In this case, the code is the answer that the student provided.
    if exercise_details["back_end"] == 'not_code':
        response = {"message": "", "test_outputs": {}}

        for test_title in exercise_details["tests"]:
            response["test_outputs"][test_title]["txt_output"] = code.strip()

        return response

    this_settings_dict = settings_dict["back_ends"][exercise_details["back_end"]]
    timeout = this_settings_dict["timeout_seconds"]

    data_dict = {"image_name": this_settings_dict["image_name"],
                 "code": code.strip(),
                 "tests": exercise_details["tests"],
                 "verification_code": verification_code,
                 "data_files": exercise_details["data_files"],
                 "output_type": exercise_details["output_type"],
                 "memory_allowed_mb": this_settings_dict["memory_allowed_mb"],
                 "timeout_seconds": timeout
                 }

    if 'MHOST' in os.environ:
        host = os.environ['MHOST']
    else:
        host = '127.0.0.1'

    response = requests.post(f"http://{host}:{os.environ['MPORT']}/exec/", json.dumps(data_dict), timeout=timeout)
    response = json.loads(response.content)

    if add_formatted_txt:
        for test_title in response["test_outputs"]:
            response["test_outputs"][test_title]["txt_output_formatted"] = format_output_as_html(response["test_outputs"][test_title]["txt_output"])

    response["all_passed"] = False # This is our default assumption.
    return response

def check_test_outputs(exercise_details, test_outputs):
    all_passed = True

    for test_title in exercise_details["tests"]:
        # It is possible we will have a submission but that the test outputs were not preserved
        # due to an issue with migrating the database in summer 2022.
        if test_title not in test_outputs:
            test_outputs[test_title] = {"passed": None, "txt_output": None, "jpg_output": None, "diff_output": None}
            continue

        test_outputs[test_title]["passed"] = False

        if exercise_details["allow_any_response"]:
            if len(test_outputs[test_title]["txt_output"]) > 0 or len(test_outputs[test_title]["jpg_output"]) > 0:
                test_outputs[test_title]["passed"] = True
        else:
            diff_output, passed = compare_outputs(exercise_details, test_outputs, test_title)
            test_outputs[test_title]["passed"] = passed
            test_outputs[test_title]["diff_output"] = diff_output

            if passed == False:
                all_passed = False

    return all_passed

def compare_outputs(exercise_details, test_outputs, test_title):
    expected_txt = exercise_details["tests"][test_title]["txt_output"]
    actual_txt = test_outputs[test_title]["txt_output"]
    expected_jpg = exercise_details["tests"][test_title]["jpg_output"]
    actual_jpg = test_outputs[test_title]["jpg_output"]

    if exercise_details["output_type"] == "txt":
        if expected_txt == actual_txt:
            return "", True
        if actual_txt == "":
            return "", False
        if len(expected_txt) > 200:
            return "", False

        diff_output, num_differences = diff_strings(expected_txt, actual_txt)

        # Only return diff output if the differences are relatively small.
        if num_differences > 20:
            diff_output = ""

        # Sometimes it's difficult for students to differentiate between spaces
        #  and tabs. This is intended to help.
        diff_output = format_output_as_html(diff_output.replace("\t", "{tab}"))

        return diff_output, False
    else:
        if expected_jpg == actual_jpg:
            return "", True
        if actual_jpg == "":
            return "", False
        elif expected_jpg == "":
            return "", True

        image_diff, diff_percent = diff_jpg(expected_jpg, actual_jpg)

        if diff_percent < 10.0:
            # Only return diff output if the differences are relatively small.
            diff_output = encode_image_bytes(convert_image_to_bytes(image_diff))
        else:
            diff_output = ""

        return diff_output, diff_percent < 0.01 # Pass if they are similar.

def encode_image_bytes(b):
    return str(base64.b64encode(b), "utf-8")

def convert_dict_to_yaml(the_dict):
    return yaml.dump(the_dict)

def load_yaml_dict(yaml_text):
    return load(yaml_text, Loader=Loader)

def escape_json_string(json_string):
    chars = ["\\","\'","\""]
    for char in chars:
        json_string = json_string.replace(char, "\\" + char)

    return json_string

def diff_strings(expected, actual):
    expected = expected.rstrip()
    actual = actual.rstrip()

    diff = difflib.ndiff(expected, actual)

    diff_output = ""
    num_chars = 0
    num_differences = 0

    for x in diff:
        sign = x[0]
        character = x[2]

        num_chars += 1

        if sign == " ":
            diff_output += character
        else:
            num_differences += 1

            if character == "\n":
                diff_output += "[\\n{}]\n".format(sign)
            else:
                diff_output += "[{}{}]".format(character, sign)

    return diff_output, (num_differences / num_chars) * 100

def render_error(handler, exception):
    handler.render("error.html", error_title="An internal error occurred", error_message=format_output_as_html(exception))

def create_id(current_objects=[], num_characters=4):
    current_ids = set([x[0] for x in current_objects])

    new_id = ''.join(random.choice(string.ascii_letters) for i in range(num_characters))
    while new_id in current_ids:
        new_id = ''.join(random.choice(string.ascii_letters) for i in range(num_characters))

    return new_id

def get_scores_download_file_name(assignment_basics):
    assignment_title = assignment_basics["title"].replace(" ", "_")
    special_chars = ["\"", "\'", "$", "&", "^", "%", "?", "*", ">", "<", "/", "\\", ":", "|"]
    for char in special_chars:
        assignment_title = assignment_title.replace(char, "")

    return f"Scores__{assignment_title}.csv"

def get_list_of_dates():
    years = []
    months = []
    days = []

    for i in range(1, 13):
        months.append("{0:02d}".format(i))
    for i in range(1, 32):
        days.append("{0:02d}".format(i))

    dateTimeObj = datetime.now()
    currYear = str(dateTimeObj.year)
    yearAbrev = int(currYear)
    for i in range(2018, yearAbrev+1):
        years.append(str(i))

    return years, months, days

def convert_string_to_date(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")

def get_client_ip_address(request):
    return request.headers.get("X-Real-IP") or \
           request.headers.get("X-Forwarded-For") or \
           request.remote_ip

def format_exercise_details(exercise_details):
    exercise_details["instructions"] = convert_markdown_to_html(convert_html_to_markdown(exercise_details["instructions"])) # Removes html markup from instructions before converting markdown to html
    exercise_details["credit"] = convert_markdown_to_html(exercise_details["credit"])
    exercise_details["solution_description"] = convert_markdown_to_html(exercise_details["solution_description"])
    exercise_details["hint"] =  convert_markdown_to_html(exercise_details["hint"])

    for test_title in exercise_details["tests"]:
        exercise_details["tests"][test_title]["txt_output"] = format_output_as_html(exercise_details["tests"][test_title]["txt_output"])
        exercise_details["tests"][test_title]["instructions"] = convert_markdown_to_html(exercise_details["tests"][test_title]["instructions"])
