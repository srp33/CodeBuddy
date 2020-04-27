import base64
import difflib
import glob
import hashlib
import html
from imgcompare import *
import json
import os
from pathlib import Path
import random
import re
import requests
from requests.exceptions import ReadTimeout
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

def exec_code(env_dict, code, problem_basics, problem_details, request=None):
    try:
        code = code + "\n\n" + problem_details["test_code"]
        settings_dict = env_dict[problem_details["environment"]]

        if request:
            for url, md5_hash in get_columns_dict(problem_details["data_urls_info"], 0, 1).items():
                cache_url = "{}://{}/data/{}/{}/{}/{}".format(
                    request.protocol,
                    request.host,
                    problem_basics["assignment"]["course"]["id"],
                    problem_basics["assignment"]["id"],
                    problem_basics["id"],
                    md5_hash)
                code = code.replace(url, cache_url)

        timeout = settings_dict["timeout_seconds"] + 2
        data_dict = {"code": code, "timeout_seconds": timeout, "output_type": problem_details["output_type"]}
        response = requests.post(settings_dict["url"], json.dumps(data_dict), timeout=timeout)

        return response.content, response.status_code != 200
    except ReadTimeout as inst:
        return "Your code did not finish executing before the time limit: {} seconds.".format(timeout).encode(), True

def test_code_txt(settings_dict, code, problem_basics, problem_details, request):
    code_output, error_occurred = exec_code(settings_dict, code, problem_basics, problem_details, request)
    code_output = code_output.decode()

    if error_occurred:
        return code_output, True, False, ""

    passed = problem_details["expected_output"] == code_output

    diff_output = ""
    if not passed and problem_details["show_expected"]:
        diff_output = diff_strings(problem_details["expected_output"], code_output)

    return code_output, error_occurred, passed, diff_output

def test_code_jpg(settings_dict, code, problem_basics, problem_details, request):
    code_output, error_occurred = exec_code(settings_dict, code, problem_basics, problem_details, request)

    if error_occurred:
        return code_output.decode(), True, False, ""

    passed, diff_image = are_images_similar(problem_details["expected_output"], code_output)

    diff_output = ""
    if not passed and problem_details["show_expected"]:
        diff_output = encode_image_bytes(convert_image_to_bytes(diff_image))

    code_output = encode_image_bytes(code_output)

    return code_output, error_occurred, passed, diff_output

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

def create_id(current_objects, num_characters=4):
    current_ids = set([x[0] for x in current_objects])

    new_id = ''.join(random.choice(string.ascii_letters) for i in range(num_characters))
    while new_id in current_ids:
        new_id = ''.join(random.choice(string.ascii_letters) for i in range(num_characters))

    return new_id

def create_md5_hash(my_string):
    return hashlib.md5(my_string.encode("utf-8")).hexdigest()

def download_file(url):
    response = requests.get(url)
    if 'Content-type' in response.headers:
        content_type = response.headers['Content-type']
    else:
        content_type = "text/plain"

    return response.content, content_type

def get_downloaded_file_path(md5_hash):
    return "/data/{}".format(md5_hash)

def write_data_file(contents, md5_hash):
    write_file(contents, get_downloaded_file_path(md5_hash), "wb")
