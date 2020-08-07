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
import sys
import time
import uuid
import yaml
from yaml import load
from yaml import Loader

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
    if len(text) == 0:
        return ""

    markdown = Markdown()
    html = markdown.convert(text)
    html = re.sub(r"<a href=\"(.+)\">", r"<a href='\1' target='_blank' rel='noopener noreferrer'>", html)
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
    code = code + "\n\n" + problem_details["test_code"]

#    if request:
#        if problem_details["data_url"] != "":
#        data_url_info = [problem_details["data_url"], problem_details["url_file_name"], problem_details["url_content_type"]]
#        if data_url_info[0] != "":
#            for url, file_name in get_columns_dict([data_url_info], 0, 1).items():
#                cache_url = "{}://{}/data/{}/{}/{}/{}".format(
#                    request.protocol,
#                    request.host,
#                    problem_basics["assignment"]["course"]["id"],
#                    problem_basics["assignment"]["id"],
#                    problem_basics["id"],
#                    file_name)
#                code = code.replace(url, cache_url)

    timeout = settings_dict["timeout_seconds"] + 2
    data_dict = {"image_name": settings_dict["image_name"],
                 "code": code,
                 "data_file_name": problem_details["data_file_name"],
                 "data_contents": problem_details["data_contents"],
                 "output_type": problem_details["output_type"],
                 "memory_allowed_mb": settings_dict["memory_allowed_mb"],
                 "timeout_seconds": timeout
                 }

    middle_layer_port = os.environ['MPORT']
    response = requests.post(f"http://127.0.0.1:{middle_layer_port}/exec/", json.dumps(data_dict), timeout=timeout)

    response_dict = json.loads(response.content)

    return response_dict["output"].strip(), response_dict["error_occurred"]

def test_code_txt(settings_dict, code, problem_basics, problem_details, request):
    code_output, error_occurred = exec_code(settings_dict, code, problem_basics, problem_details, request)

    if error_occurred:
        return code_output, True, False, ""

    passed = problem_details["expected_output"] == code_output

    return code_output, error_occurred, passed, find_differences_txt(problem_details, code_output, passed)

def test_code_jpg(settings_dict, code, problem_basics, problem_details, request):
    code_output, error_occurred = exec_code(settings_dict, code, problem_basics, problem_details, request)

    if error_occurred:
        return format_output_as_html(code_output), True, False, ""

    diff_percent, diff_image = diff_jpg(problem_details["expected_output"], code_output)
    passed = does_image_pass(diff_percent)

    return code_output, error_occurred, passed, find_differences_jpg(problem_details, passed, diff_image)

def find_differences_txt(problem_details, code_output, passed):
    diff_output = ""

    if not passed and problem_details["show_expected"]:
        diff_output = diff_strings(problem_details["expected_output"], code_output)

    return diff_output

def find_differences_jpg(problem_details, passed, diff_image):
    diff_output = ""
    if not passed and problem_details["show_expected"]:
        diff_output = encode_image_bytes(convert_image_to_bytes(diff_image))
    return diff_output

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

def create_id(current_objects=[], num_characters=4):
    current_ids = set([x[0] for x in current_objects])

    new_id = ''.join(random.choice(string.ascii_letters) for i in range(num_characters))
    while new_id in current_ids:
        new_id = ''.join(random.choice(string.ascii_letters) for i in range(num_characters))

    return new_id

#def create_md5_hash(my_string):
#    return hashlib.md5(my_string.encode("utf-8")).hexdigest()

def download_file(url):
    response = requests.get(url)

    #if 'Content-type' in response.headers:
    #    content_type = response.headers['Content-type']
    #else:
    #    content_type = "text/plain"

    #return response.content, content_type, get_url_extension(url)
    return response.content

#def get_url_extension(url):
#    file_name = os.path.basename(url)
#    if "." in file_name:
#        return "." + file_name.split(".")[-1]
#    return ""

#def get_downloaded_file_path(file_name):
#    return "/data/{}".format(file_name)

#def write_data_file(contents, file_name):
#    # First delete any old files to prevent stale file buildup
#    for f in glob.glob("/data/*"):
#        if is_old_file(f):
#            os.remove(f)
#
#    write_file(contents, get_downloaded_file_path(file_name), "wb")

def show_hidden(request_handler):
    if "show_hidden" not in request_handler.request.query_arguments:
        return False
    return request_handler.request.query_arguments["show_hidden"][0].decode().lower() == "true"

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
