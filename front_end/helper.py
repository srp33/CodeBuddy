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

def convert_markdown_to_html(text):
    if not text or len(text) == 0:
        return ""

    markdown = Markdown()
    html = re.sub(r"youtube:([-_a-zA-Z0-9]+)", r"<iframe width='800' height='550' src='https://www.youtube.com/embed/\1?controls=1'></iframe>", text)
    html = markdown.convert(html)
    html = re.sub(r"<a href=\"([^\"]+)\">", r"<a href='\1' target='_blank' rel='noopener noreferrer'>", html)
    return html

def format_output_as_html(output):
    return html.escape(output).replace(" ", "&nbsp;").replace("\t", "&emsp;").replace("\n", "<br />")

# Kudos: https://arcpy.wordpress.com/2012/05/11/sorting-alphanumeric-strings-in-python/
def sort_nicely(l):
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key = alphanum_key)

#def sort_nested_by_index(nested_list, index):
#    l_dict = {}
#    for row in nested_list:
#        l_dict[row[index]] = row
#
#    sorted_list = []
#    for key in sort_nicely(l_dict):
#        sorted_list.append(l_dict[key])
#
#    return sorted_list

def get_columns_dict(nested_list, key_col_index, value_col_index):
    columns_dict = {}
    for row in nested_list:
        columns_dict[row[key_col_index]] = row[value_col_index]
    return columns_dict

def exec_code(settings_dict, code, problem_basics, problem_details, request=None):
    this_settings_dict = settings_dict["back_ends"][problem_details["back_end"]]
    code = code + "\n\n" + problem_details["test_code"]

    if problem_details["back_end"] in ['free_response', 'any_response']:
        # In this case, the code is the answer that the student provided.
        return code.strip(), ""

    timeout = this_settings_dict["timeout_seconds"] + 2
    data_dict = {"image_name": this_settings_dict["image_name"],
                 "code": code,
                 "data_file_name": problem_details["data_file_name"],
                 "data_contents": problem_details["data_contents"],
                 "output_type": problem_details["output_type"],
                 "memory_allowed_mb": this_settings_dict["memory_allowed_mb"],
                 "timeout_seconds": timeout
                 }

    middle_layer_port = os.environ['MPORT']
    response = requests.post(f"http://127.0.0.1:{middle_layer_port}/exec/", json.dumps(data_dict), timeout=timeout)
    response_dict = json.loads(response.content)

    return response_dict["text_output"], response_dict["image_output"]

def check_problem_output(problem_details, actual_text, actual_image):
    if problem_details["back_end"] == "any_response" and len(actual_text) > 0 or len(actual_image) > 0:
        return "", True

    if problem_details["output_type"] == "txt":
        expected_text = problem_details["expected_text_output"]

        if expected_text == actual_text:
            return "", True
        if actual_text == "":
            return "", False

        diff_output, num_differences = diff_strings(expected_text, actual_text)

        # Only return diff output if the differences are relatively small.
        if num_differences > 20:
            diff_output = ""

        return diff_output, False
    else:
        expected_image = problem_details["expected_image_output"]

        if expected_image == actual_image:
            return "", True
        if actual_image == "":
            return "", False

        diff_image, diff_percent = diff_jpg(expected_image, actual_image)

        diff_output = ""
        max_diff_percent = 1.0
        if diff_percent > max_diff_percent:
            # Only return diff output if the differences are relatively small.
            diff_output = encode_image_bytes(convert_image_to_bytes(diff_image))

        return diff_output, diff_percent < max_diff_percent # Pass if they are similar enough.

def encode_image_bytes(b):
    return str(base64.b64encode(b), "utf-8")

def convert_dict_to_yaml(the_dict):
    return yaml.dump(the_dict)

def load_yaml_dict(yaml_text):
    return load(yaml_text, Loader=Loader)

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

def download_file(url):
    return requests.get(url).content

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
