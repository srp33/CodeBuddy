# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

import base64
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime, timedelta, timezone
import difflib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import glob
import hashlib
import html
from imgcompare import *
from io import StringIO
import json
import logging
import markdown2
import os
from pathlib import Path
import pytz
import random
import re
import requests
from requests.exceptions import *
import secrets
import smtplib, ssl 
import sqlite3
import string
import subprocess
from tornado.web import RequestHandler
import traceback
import ujson
import urllib.parse
import yaml
from yaml import load
from yaml import Loader

def run_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return result.stdout.decode()

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
    # if 'ROOT' in os.environ:
    #     file_path = os.path.join(os.environ['ROOT'], file_path)

    with open(file_path, mode) as the_file:
        return the_file.read()

def convert_markdown_to_html(text):
    if not text or len(text) == 0:
        return ""

    html = re.sub(r"youtube:([-_a-zA-Z0-9]+)", r"<iframe width='800' height='550' src='https://www.youtube.com/embed/\1?controls=1' title='Embedded video content'></iframe>\n", text)
    html = re.sub(r"panopto:([a-zA-Z0-9\.]+.panopto.com)\/([-_a-z0-9]+)", r"<p style='text-align: left;'>\n<iframe id='panopto_iframe' style='border: 1px solid #464646;' title='Embedded video content' src='https://\1/Panopto/Pages/Embed.aspx?id=\2&amp;autoplay=false&amp;offerviewer=true&amp;showtitle=false&amp;showbrand=false&amp;captions=false&amp;interactivity=none' width='100%' height='450' allowfullscreen='allowfullscreen' allow='autoplay'></iframe>\n</p>\n", html)
    html = re.sub(r'```(.+?)```', r"<code>\1</code>", html)  # Formats single line code chunks
    html = re.sub(r'```([\s\S]*?)```', r"<pre><code>\1</code></pre>", html) # Formats multiline code blocks
    html = re.sub(r'<pre><code>\n', r"<pre><code>", html) # Removes extra newline, if present
    html = markdown2.markdown(html, extras=["tables"])
    html = re.sub(r"<a href=\"([^\"]+)\">", r"<a href='\1' target='_blank' rel='noopener noreferrer'>", html)

    html = re.sub(r'^\s*<p>(.*?)</p>\s+$', r'\1', html)

    return html

# This function addresses a temporary problem and may be removed when it is no longer needed.
# def remove_html_tags(text):
#     #text = text.replace("<div><br></div>", "\n\n")
#     text = text.replace("<div>", "\n")
#     text = re.sub(r"<[^>]*>", "", text)

#     return text

def format_output_as_html(output):
    return html.escape(output).replace(" ", "&nbsp;").replace("\t", "&emsp;").replace("\n", "<br />").replace("`", "&#96;")

# Kudos: https://arcpy.wordpress.com/2012/05/11/sorting-alphanumeric-strings-in-python/
def sort_nicely(l):
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key = alphanum_key)

def sort_list_of_dicts_nicely(lst, keys):
    sort_dict = {}
    for item in lst:
        sort_key = "__".join([str(item[key]) for key in keys])
        sort_dict[sort_key] = item

    sorted_list = []
    for dict_key in sort_nicely(sort_dict.keys()):
        sorted_list.append(sort_dict[dict_key])

    return sorted_list

def get_columns_dict(nested_list, key_col_index, value_col_index):
    columns_dict = {}
    for row in nested_list:
        columns_dict[row[key_col_index]] = row[value_col_index]
    return columns_dict

async def exec_code(settings_dict, code, verification_code, exercise_details, add_formatted_txt = False):
    # In this case, the code is the answer that the student provided.
    if exercise_details["back_end"] == "not_code":
        response = {"message": "", "test_outputs": {}}

        for test_title in exercise_details["tests"]:
            response["test_outputs"][test_title] = {"txt_output": code.strip(), "jpg_output": "", "txt_output_formatted": format_output_as_html(code.strip()), "diff_output": ""}

        return response
    
    if exercise_details["back_end"] == "python_testing_only":
        if settings_dict["mode"] != "development":
            return {"message": "The python_testing_only back end can only be executed in development mode.", "test_outputs": {}}

        response = {"message": "", "test_outputs": {}}

        for test_title in exercise_details["tests"]:
            code_to_execute = exercise_details["tests"][test_title]["before_code"].strip() + "\n\n" + code + "\n\n" + exercise_details["tests"][test_title]["after_code"].strip()

            output = execute_python_string_for_testing(code_to_execute)

            response["test_outputs"][test_title] = {"txt_output": output.strip(), "jpg_output": "", "txt_output_formatted": format_output_as_html(output.strip()), "diff_output": ""}

        return response

    back_end_config = get_back_end_config(exercise_details["back_end"])

    if settings_dict["mode"] == "development":
        timeout = -1
    else:
        timeout = back_end_config["timeout_seconds"]

    data_dict = {"image_name": f"codebuddy/{exercise_details['back_end']}_{settings_dict['mode']}",
                 "code": code.strip(),
                 "tests": exercise_details["tests"],
                 "verification_code": verification_code,
                 "data_files": exercise_details["data_files"],
                 "output_type": exercise_details["output_type"],
                 "memory_allowed_mb": back_end_config["memory_allowed_mb"],
                 "timeout_seconds": timeout
                 }

    request_timeout = 30
    if settings_dict["mode"] != "development":
        request_timeout = timeout

    # This environment variable is used when Docker is executed on a Mac.
    m_host = os.getenv("MHOST")
    if not m_host:
        m_host = settings_dict["m_host"]
    
    #TODO: Move try/except block here for ReadTimeout?
    response = requests.post(f"http://{m_host}:{settings_dict['m_port']}/exec/", json.dumps(data_dict, default=str), timeout=request_timeout)

    response = ujson.loads(response.content)

    if "test_outputs" in response:
        if add_formatted_txt:
            for test_title in response["test_outputs"]:
                response["test_outputs"][test_title]["txt_output_formatted"] = format_output_as_html(response["test_outputs"][test_title]["txt_output"])
    else:
        # We are using this for debugging. If something goes awry on the
        # back end, this will help us see what happened.
        for test_title in exercise_details["tests"]:
            response["test_outputs"][test_title] = {"txt_output": response["message"], "jpg_output": "", "txt_output_formatted": "", "diff_output": ""}

    response["all_passed"] = False # This is our default assumption.
    return response

def check_test_outputs(exercise_details, test_outputs):
    all_passed = True

    for test_title in exercise_details["tests"]:
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
    if exercise_details["output_type"] == "txt":
        expected_txt = exercise_details["tests"][test_title]["txt_output"]
        actual_txt = test_outputs[test_title]["txt_output"]

        if expected_txt == actual_txt:
            return "", True
        if actual_txt == "":
            return "placeholder", False
        #if len(expected_txt) > 200:
        #    return "", False
        return "placeholder", False

        #diff_output, num_differences = diff_strings(expected_txt, actual_txt)

        # Only return diff output if the differences are relatively small.
        #if num_differences > 20:
        #    diff_output = ""

        #return diff_output, False
    else:
        expected_jpg = exercise_details["tests"][test_title]["jpg_output"]
        actual_jpg = test_outputs[test_title]["jpg_output"]

        if expected_jpg == actual_jpg:
            return "", True
        if actual_jpg == "":
            return "", False
        elif expected_jpg == "":
            return "", True

        try:
            image_diff, diff_percent = diff_jpg(expected_jpg, actual_jpg)

            if diff_percent < 10.0:
                # Only return diff output if the differences are relatively small.
                diff_output = encode_image_bytes(convert_image_to_bytes(image_diff))
            else:
                diff_output = ""

            return diff_output, diff_percent < 0.01 # Pass if they are similar enough.
        except:
            return "", False

# This prevents students from seeing information they should not be able to see.
def sanitize_test_outputs(exercise_details, test_outputs):
    for test_title in exercise_details["tests"]:
        if not exercise_details["tests"][test_title]["can_see_code_output"]:
            test_outputs[test_title]["txt_output"] = ""
            test_outputs[test_title]["txt_output_formatted"] = ""
            test_outputs[test_title]["jpg_output"] = ""
            test_outputs[test_title]["diff_output"] = ""

def execute_python_string_for_testing(python_code):
    # Create StringIO objects to capture the output and error
    output = StringIO()
    error = StringIO()

    # Redirect stdout and stderr to the StringIO objects
    with redirect_stdout(output), redirect_stderr(error):
        try:
            exec(python_code)
        except Exception as e:
            print(traceback.format_exc(), file=error)

    # Concatenate the output and error into a single string
    return output.getvalue() + error.getvalue()

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

def redirect_to_login(handler, redirect_path):
    handler.set_secure_cookie("redirect_path", redirect_path)

    if handler.settings_dict["mode"] == "production":
        handler.redirect("/login")
    else:
        handler.redirect("/devlogin")
        # handler.redirect("/login")

def render_error(handler, exception):
    # This makes it so we see the error message on the console.
    print(exception)

    # This tells the client that an application error occurred.
    handler.set_status(500)

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

    return f"Scores__{assignment_title}__{get_formatted_datetime()}.tsv"

def get_client_ip_address(request):
    return request.headers.get("X-Real-IP") or \
           request.headers.get("X-Forwarded-For") or \
           request.remote_ip

def format_exercise_details(exercise_details, course_basics, assignment_basics, user_info, content, next_prev_exercises=None, format_tests=True, format_data=False):
    exercise_details["credit"] = convert_markdown_to_html(exercise_details["credit"])

    if exercise_details["back_end"] != "multiple_choice":
        exercise_details["solution_description"] = convert_markdown_to_html(exercise_details["solution_description"])

    exercise_details["hint"] =  convert_markdown_to_html(exercise_details["hint"])

    modify_what_students_see(exercise_details, user_info)

    # Do formatting
    for test_title in exercise_details["tests"]:
        if format_tests:
            exercise_details["tests"][test_title]["before_code"] = format_output_as_html(exercise_details["tests"][test_title]["before_code"])
            exercise_details["tests"][test_title]["after_code"] = format_output_as_html(exercise_details["tests"][test_title]["after_code"])

            exercise_details["tests"][test_title]["txt_output_formatted"] = format_output_as_html(exercise_details["tests"][test_title]["txt_output"])

        exercise_details["tests"][test_title]["instructions"] = convert_markdown_to_html(exercise_details["tests"][test_title]["instructions"])

    if "[reflection_prompt]" in exercise_details["instructions"]:
        if not next_prev_exercises or not next_prev_exercises["previous"]:
            prompt = "Error: [reflection_prompt] can only be used in the instructions when an exercise is *not* the first in an assignment."
        else:
            prev_exercise_details = content.get_exercise_details(course_basics, assignment_basics, next_prev_exercises["previous"]["id"])
            modify_what_students_see(prev_exercise_details, user_info)

            # https://dl.acm.org/doi/pdf/10.1145/3313831.3376857
            blurb1 = "If you have not already done so, complete the [previous_exercise_link]. "
            #blurb2 = "Then, for the current exercise, provide an essay response (1-3 medium-sized paragraphs) that answers any or all of the following:\n\n* What did you learn from reviewing the other solutions?\n* How does your strategy compare to the others'?\n* How did the code formatting or variable naming compare among the solutions?"
            blurb2 = "Then, for the current exercise, describe what you learned from comparing the solutions. What programming strategies were used? How are they similar to or different from each other? "
            blurb3 = "Then, for the current exercise, describe your programming strategy. What was your approach? What other approaches might have been used? "
            blurb4 = "Your response should be at least 2-3 sentences in length."

            if prev_exercise_details["show_instructor_solution"]:
                if prev_exercise_details["show_peer_solution"]:
                    exercise_details["instructions"] = exercise_details["instructions"].replace("[reflection_prompt]", blurb1 + "On that page, you should see links that allow you to see the instructor's solution and an anonymized solution from a peer. Click on those links and compare your solution against theirs. " + blurb2 + blurb4)
                else:
                    exercise_details["instructions"] = exercise_details["instructions"].replace("[reflection_prompt]", blurb1 + "On that page, you should see a link that allows you to see the instructor's solution. Click on that link and compare your solution against the instructor's. " + blurb2 + blurb4)
            elif prev_exercise_details["show_peer_solution"]:
                exercise_details["instructions"] = exercise_details["instructions"].replace("[reflection_prompt]", blurb1 + "On that page, you should see links that allow you to see an anonymized solution from a peer. Click on that link and compare your solution against theirs. " + blurb2 + blurb4)
            else:
                exercise_details["instructions"] = exercise_details["instructions"].replace("[reflection_prompt]", blurb1 + blurb3 + blurb4)

    if next_prev_exercises != None:
        if next_prev_exercises["previous"]:
            link_html = f"<a href='/exercise/{course_basics['id']}/{assignment_basics['id']}/{next_prev_exercises['previous']['id']}'>previous exercise</a>"
            exercise_details["instructions"] = exercise_details["instructions"].replace("[previous_exercise_link]", link_html)

            if "[copy_previous]" in exercise_details["instructions"]:
                previous_submission_code = content.get_most_recent_submission_code(course_basics['id'], assignment_basics['id'], next_prev_exercises["previous"]["id"], user_info["user_id"])

                if previous_submission_code == "":
                    exercise_details["instructions"] = exercise_details["instructions"].replace("[copy_previous]", "")
                else:
                    # We need to replace backticks with a placeholder because backticks can cause a problem on the Javascript side. We replace backslash characters as well because they do not get translated properly on the front end.
                    previous_submission_code = previous_submission_code.replace("`", "_bcktck_").replace("\\", "_xyzslashxyz_")

                    exercise_details["previous_submission_code"] = previous_submission_code

    exercise_details["instructions"] = exercise_details["instructions"].replace("[previous_exercise_link]", "").replace("[copy_previous]", "") # This is just in case they added it when it is the first exercise.

    exercise_details["instructions"] = convert_markdown_to_html(exercise_details["instructions"])

    for file_name in exercise_details["data_files"]:
        if file_name.endswith(".hide"):
            exercise_details["data_files"][file_name] = ""

def set_assignment_due_date_passed(assignment_details):
    assignment_details["due_date_passed"] = None
    if assignment_details["due_date"]:
        assignment_details["due_date_passed"] = get_current_datetime() > assignment_details["due_date"]

def modify_what_students_see(exercise_details, user_info):
    exercise_details["show_instructor_solution"] = False
    exercise_details["show_peer_solution"] = False

    if exercise_details["back_end"] != "not_code":
        what_students_see = exercise_details["what_students_see_after_success"]

        if what_students_see in (1, 3) or (what_students_see == 4 and user_info["research_cohort"] == "A") or (what_students_see == 6 and user_info["research_cohort"] == "B") or (what_students_see == 8 and user_info["research_cohort"] == "A") or (what_students_see == 9 and user_info["research_cohort"] == "B"):
            exercise_details["show_instructor_solution"] = True

        if what_students_see in (2, 3) or (what_students_see == 5 and user_info["research_cohort"] == "A") or (what_students_see == 7 and user_info["research_cohort"] == "B") or (what_students_see == 8 and user_info["research_cohort"] == "A") or (what_students_see == 9 and user_info["research_cohort"] == "B"):
            exercise_details["show_peer_solution"] = True

    for test_title in exercise_details["tests"]:
        if not exercise_details["tests"][test_title]["can_see_test_code"]:
            exercise_details["tests"][test_title]["before_code"] = ""
            exercise_details["tests"][test_title]["after_code"] = ""

        if not exercise_details["tests"][test_title]["can_see_expected_output"]:
            exercise_details["tests"][test_title]["txt_output"] = ""
            exercise_details["tests"][test_title]["jpg_output"] = ""

def open_db(db_file_path):
    # if 'ROOT' in os.environ:
    #     db_file_path = os.path.join(os.environ['ROOT'], db_file_path)

    # This enables auto-commit.
    return sqlite3.connect(
        db_file_path,
        isolation_level = None,
        detect_types = sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES,
        timeout = 30,
    )

def log_page_access(handler, additional_message=None):
    # The request time is in seconds
    # logging_message = f"{handler.get_browser_locale().code}\t{handler.request.uri}\t{handler.request.method}\t{handler.request.remote_ip}\t{round(handler.request.request_time(), 3)}"
    logging_message = f"{handler.get_browser_locale().code}\t{handler.request.uri}\t{handler.request.method}\t{get_client_ip_address(handler.request)}\t{round(handler.request.request_time(), 3)}"

    if additional_message:
        logging_message = f"{logging_message}\t{additional_message}"

    logging.info(logging_message)

def get_assignment_status(handler, course_id, assignment_id, assignment_details, curr_datetime, user_id):
    client_ip = get_client_ip_address(handler.request)

    if assignment_details["allowed_ip_addresses"] and assignment_details["allowed_ip_addresses"] != "" and client_ip not in assignment_details["allowed_ip_addresses_list"]:
        return "restricted_ip"
    elif assignment_details["start_date"] and assignment_details["start_date"] > curr_datetime and not handler.content.student_has_early_exception(course_id, assignment_id, user_id):
        return "start_date"
    elif assignment_details["due_date"] and assignment_details["due_date"] < curr_datetime and not assignment_details["allow_late"] and not assignment_details["view_answer_late"]:
        return "due_date"
    elif handler.user_info["user_id"] not in list(map(lambda x: x[0], handler.content.get_registered_students(course_id))):
        return "not_registered_for_course"

    return "render"

async def execute_and_save_exercise(settings_dict, content, exercise_basics, exercise_details):
    exec_response = await exec_code(settings_dict, exercise_details["solution_code"], "", exercise_details, True)

    if exec_response["message"] == "":
        has_non_empty_output = False

        for test_title in exec_response["test_outputs"]:
            txt_output = exec_response["test_outputs"][test_title]["txt_output"]
            jpg_output = exec_response["test_outputs"][test_title]["jpg_output"]

            exercise_details["tests"][test_title]["txt_output"] = txt_output
            exercise_details["tests"][test_title]["txt_output_formatted"] = exec_response["test_outputs"][test_title]["txt_output_formatted"]
            exercise_details["tests"][test_title]["jpg_output"] = jpg_output

            if txt_output != "" or jpg_output != "":
                has_non_empty_output = True

        if has_non_empty_output or exercise_details["allow_any_response"]:
            return content.save_exercise(exercise_basics, exercise_details), True
        else:
            return "No output was produced for any test.", False
    else:
        return exec_response["message"], False

def is_valid_email_address(email_address):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email_address) is not None

def send_email(from_name, from_address, to_name, to_address, smtp_server, smtp_port, subject, body):
    msg = MIMEMultipart()
    msg["From"] = formataddr((from_name, from_address))
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        context = ssl.create_default_context()
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls(context = context)

        server.sendmail(from_address, to_address, msg.as_string())
        success = True
    except Exception as e:
        print(f"Error: {e}")
        logging.error(traceback.format_exc())
        success = False
    finally:
        server.quit()

    return success

def md5_hash_string(string):
    return hashlib.md5(string.encode()).hexdigest()

def get_back_ends_dict(production_mode):
    back_ends_dict = {}

    for back_end_dir_path in glob.glob("../back_ends/*"):
        back_end_name = os.path.basename(back_end_dir_path)
        back_end_config = load_yaml_dict(read_file(f"{back_end_dir_path}/config.yaml"))

        if production_mode and back_end_name == "python_testing_only":
            continue

        back_ends_dict[back_end_name] = back_end_config

    return back_ends_dict

def get_back_end_config(name):
    return load_yaml_dict(read_file(f"../back_ends/{name}/config.yaml"))

async def should_use_virtual_assistant(handler, course_id, course_details, assignment_details, exercise_basics, exercise_details, user_info):
    hide_arg = handler.get_query_argument("hide_va", default=None)
    if hide_arg and hide_arg == "true":
        return False

    if not course_details["virtual_assistant_config"]:
        return False

    if exercise_basics["enable_pair_programming"]:
        return False
    
    if exercise_details["back_end"] == "not_code":
        return False

    if assignment_details["use_virtual_assistant"] == 1:
        return True

    has_special_permission = handler.is_administrator or await handler.is_instructor_for_course(course_id) or await handler.is_assistant_for_course(course_id)

    if has_special_permission and (assignment_details["use_virtual_assistant"] == 2 or ["use_virtual_assistant"] == 3):
        return True

    return (assignment_details["use_virtual_assistant"] == 2 and user_info["research_cohort"] == "A") or (assignment_details["use_virtual_assistant"] == 3 and user_info["research_cohort"] == "B")

def get_current_datetime():
    return datetime.now(timezone.utc)

def get_formatted_datetime():
    return get_current_datetime().strftime("%Y%m%d_%H%M%S")

def convert_string_to_datetime(date_str):
    if date_str:
        # Sometimes there are decimal points on the end of dates.
        date_str = date_str.split(".")[0]

        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

def localize_datetime(dtime):
    if dtime:
        return pytz.utc.localize(dtime)

    return dtime

def get_student_timer_status(content, course_id, assignment_id, assignment_details, student_id, user_start_time=None, user_ended_early=None):
    if user_start_time == None:
        user_start_time, user_ended_early = content.get_user_assignment_timer_status(course_id, assignment_id, student_id)

    hours = assignment_details["hour_timer"]
    minutes = assignment_details["minute_timer"]

    if student_id in assignment_details["student_timer_exceptions"]:
        hours = assignment_details["student_timer_exceptions"][student_id][0]
        minutes = assignment_details["student_timer_exceptions"][student_id][1]

    if user_start_time == None:
        return "timer_not_started", None, hours, minutes, None

    if user_ended_early == True:
        return "timer_expired", user_start_time, None, None, None

    deadline = user_start_time + timedelta(hours = hours, minutes = minutes)

    if deadline < get_current_datetime():
        return "timer_expired", user_start_time, None, None, None

    return "timer_in_progress", user_start_time, None, None, deadline

def generate_unique_id(characters_per_segment, num_segments, delimiter=""):
    # Create a character set of uppercase letters and digits. Avoid characters that are difficult to distinguish between.
    characters = [x for x in string.ascii_letters if x.isupper() and x != "O"]
    for i in range(1, 10):
        characters.append(str(i))

    # Separate the id into segments
    unique_id_segments = []
    for i in range(num_segments):
        segment = ''.join(secrets.choice(characters) for j in range(characters_per_segment))
        unique_id_segments.append(segment)

    return delimiter.join(unique_id_segments)

def split_str_by_positions(my_str, characters_per_segment, delimiter):
    segments = []

    for i in range(1, int(len(my_str) / characters_per_segment) + 1):
        segments.append(my_str[:characters_per_segment])
        my_str = my_str[characters_per_segment:]

    return delimiter.join(segments)

def adjust_assignment_score(score, custom_scoring):
    if not custom_scoring or len(custom_scoring) == 0:
        # There is no custom scoring defined.
        return(score)
    else:
        # Apply the custom scoring.
        ranges = json.loads(custom_scoring)

        # Start at the top of the range so that if the score
        # falls at the lower threshold, they will receive
        # more points.
        for index, range in enumerate(ranges[::-1]):
            if index == 0:
                if score >= range[0] and score <= range[1]:
                    return range[2]
            else:
                if score >= range[0] and score < range[1]:
                    return range[2]

        # Return the unadjusted score if there was no matching range.
        return(score)
    
def detect_ai(code):
    num_comment_lines = 0
    num_comment_lines_with_ai_marker = 0

    for line in code.split("\n"):
        line = line.strip()

        if re.search(r"^(#|\/\/)", line):
            num_comment_lines += 1

            if re.search(r"(#|\/\/)$", line):
                num_comment_lines_with_ai_marker += 1
    
    if num_comment_lines > 0:
        proportion = num_comment_lines_with_ai_marker / num_comment_lines

        if proportion > 0.5:
            return True
    
    return False