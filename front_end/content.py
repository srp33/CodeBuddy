import glob
from helper import *
import io
import os
import yaml
from yaml import load
from yaml import Loader
import zipfile
import sqlite3

def get_environments():
    return load_yaml_dict(read_file("/Environments.yaml"))

def create_database():
    print(os.access("/submissions", os.W_OK))
    print("directory: " + os.getcwd())
    sqliteConnection = sqlite3.connect("/submissions/test.db")
    try:
        #sqliteConnection = sqlite3.connect("test.db")
        cursor = sqliteConnection.cursor()
        print("Database created and successfully connected to SQLite")

        #sqlite_select_Query = "select sqlite_version();"
        cursor.execute("select sqlite_version();")
        record = cursor.fetchall()
        print("SQLite database version is: ", record)
        cursor.close()

    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)

    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("The SQLite connection is closed")
    # db = sqlite3.connect("test.db")
    # if not db:
    #     create_table(db)

#  def create_table(table_name):
#      db = sqlite3.connect("test.db")
#      #if not db:
#      #    create_table(db)
#      #Create database table given a database connection 'db'.

#      cursor = db.cursor()
#      cursor.execute("DROP TABLE IF EXISTS " + table_name)
#      cursor.execute("""
#      CREATE TABLE table_name (
#         thing text
#      )
#      """)



def get_root_dir_path():
    return "/course"

def get_courses(show_hidden=True):
    course_ids = [os.path.basename(x) for x in glob.glob("{}/*".format(get_root_dir_path()))]

    courses = []
    for course_id in course_ids:
        course_basics = get_course_basics(course_id)
        if course_basics["visible"] or show_hidden:
            courses.append([course_id, course_basics])

    return sort_nested_list(courses)

def get_assignments(course, show_hidden=True):
    assignments = []

    for assignment_dir_path in glob.glob(get_course_dir_path(course) + "*"):
        if os.path.isdir(assignment_dir_path):
            assignment_id = os.path.basename(assignment_dir_path)
            assignment_basics = get_assignment_basics(course, assignment_id)
            if assignment_basics["visible"] or show_hidden:
                assignments.append([assignment_id, assignment_basics])

    return sort_nested_list(assignments)

def get_problems(course, assignment, show_hidden=True):
    problems = []

    for problem_dir_path in glob.glob(get_root_dir_path() + f"/{course}/{assignment}/*"):
        if os.path.isdir(problem_dir_path):
            problem_id = os.path.basename(problem_dir_path)
            problem_basics = get_problem_basics(course, assignment, problem_id)
            if problem_basics["visible"] or show_hidden:
                problems.append([problem_id, problem_basics])

    return sort_nested_list(problems)

def get_submissions_basic(course, assignment, problem, user):
    submissions = []

    for submission_path in glob.glob(get_submission_dir_path(course, assignment, problem, user)):
        submission_id = int(os.path.basename(submission_path)[:-5])
        submission_dict = load_yaml_dict(read_file(submission_path))
        submissions.append([submission_id, submission_dict["date"], submission_dict["passed"]])

    return sorted(submissions, key = lambda x: x[0], reverse=True)

def get_course_dir_path(course):
    return get_root_dir_path() + f"/{course}/"

def get_assignment_dir_path(course, assignment):
    return get_root_dir_path() + f"/{course}/{assignment}/"

def get_problem_dir_path(course, assignment, problem):
    return get_root_dir_path() + f"/{course}/{assignment}/{problem}/"

def get_submission_dir_path(course, assignment, problem, user):
    return f"/submissions/{course}/{assignment}/{problem}/{user}/*"

def get_submission_file_path(course, assignment, problem, user, submission_id):
    return f"/submissions/{course}/{assignment}/{problem}/{user}/{submission_id}.yaml"

def get_course_basics(course):
    if not course:
        course = create_id(get_courses())

    file_path = get_course_dir_path(course) + "basics"
    course_dict = {"id": course, "title": "", "visible": True, "exists": False}

    if os.path.exists(file_path):
        course_dict = load_yaml_dict(read_file(file_path))
        course_dict["exists"] = True

    return course_dict

def get_assignment_basics(course, assignment):
    if not assignment:
        assignment = create_id(get_assignments(course))

    file_path = get_assignment_dir_path(course, assignment) + "basics"
    course_basics = get_course_basics(course)
    assignment_dict = {"id": assignment, "title": "", "visible": True, "exists": False, "course": course_basics}

    if os.path.exists(file_path):
        assignment_dict = load_yaml_dict(read_file(file_path))
        assignment_dict["exists"] = True
        assignment_dict["course"] = course_basics

    return assignment_dict

def get_problem_basics(course, assignment, problem):
    if not problem:
        problem = create_id(get_problems(course, assignment))

    file_path = get_problem_dir_path(course, assignment, problem) + "basics"
    assignment_basics = get_assignment_basics(course, assignment)
    problem_dict = {"id": problem, "title": "", "visible": True, "exists": False, "assignment": assignment_basics}

    if os.path.exists(file_path):
        problem_dict = load_yaml_dict(read_file(file_path))
        problem_dict["exists"] = True
        problem_dict["assignment"] = assignment_basics

    return problem_dict

def get_next_prev_problems(course, assignment, problem, problems):
    prev_problem = None
    next_problem = None

    if len(problems) > 0 and problem:
        this_problem = [i for i in range(len(problems)) if problems[i][0] == problem]
        if len(this_problem) > 0:
            this_problem_index = [i for i in range(len(problems)) if problems[i][0] == problem][0]

            if len(problems) >= 2 and this_problem_index != 0:
                prev_problem = problems[this_problem_index - 1][1]

            if len(problems) >= 2 and this_problem_index != (len(problems) - 1):
                next_problem = problems[this_problem_index + 1][1]

    return {"previous": prev_problem, "next": next_problem}

def get_next_submission_id(course, assignment, problem, user):
    return get_num_submissions(course, assignment, problem, user) + 1

def get_last_submission(course, assignment, problem, user):
    last_submission_id = get_num_submissions(course, assignment, problem, user)
    file_path = f"/submissions/{course}/{assignment}/{problem}/{user}/{last_submission_id}.yaml"
    last_submission = load_yaml_dict(read_file(file_path))

    return last_submission

def get_num_submissions(course, assignment, problem, user):
    return len(glob.glob(f"{get_submission_dir_path(course, assignment, problem, user)}"))

def get_submission_info(course, assignment, problem, user, submission_id):
    return load_yaml_dict(read_file(get_submission_file_path(course, assignment, problem, user, submission_id)))

def get_course_details(course, format_output=False):
    file_path = get_course_dir_path(course) + "details"
    exists = os.path.exists(file_path)
    course_dict = {"introduction": ""}

    if exists:
        course_dict = load_yaml_dict(read_file(file_path))
        if format_output:
            course_dict["introduction"] = convert_markdown_to_html(course_dict["introduction"])

    return course_dict

def get_assignment_details(course, assignment, format_output=False):
    file_path = get_assignment_dir_path(course, assignment) + "details"
    exists = os.path.exists(file_path)
    assignment_dict = {"introduction": ""}

    if exists:
        assignment_dict = load_yaml_dict(read_file(file_path))
        if format_output:
            assignment_dict["introduction"] = convert_markdown_to_html(assignment_dict["introduction"])

    return assignment_dict

def get_problem_details(course, assignment, problem, format_content=False, parse_data_urls=False):
    file_path = get_problem_dir_path(course, assignment, problem) + "details"

    if os.path.exists(file_path):
        problem_dict = load_yaml_dict(read_file(file_path))

        if format_content:
            problem_dict["instructions"] = convert_markdown_to_html(problem_dict["instructions"])
            problem_dict["credit"] = convert_markdown_to_html(problem_dict["credit"])

            if "answer_description" not in problem_dict:
                problem_dict["answer_description"] = ""
            else:
                problem_dict["answer_description"] = convert_markdown_to_html(problem_dict["answer_description"])

        if parse_data_urls:
            problem_dict["data_urls"] = "\n".join([x[0] for x in problem_dict["data_urls_info"]])

        # This was added later, so adding it for backward compatibility
        if "answer_description" not in problem_dict:
            problem_dict["answer_description"] = ""
        if "show_answer" not in problem_dict:
            problem_dict["show_answer"] = ""

    else:
        problem_dict = {"instructions": "", "environment": "r_back_end",
            "output_type": "txt", "answer_code": "", "answer_description": "", "test_code": "",
            "credit": "", "show_expected": True, "show_test_code": True, "show_answer": True,
            "expected_output": "", "data_urls": "", "data_urls_info": []}

    return problem_dict

def sort_nested_list(nested_list, key="title"):
    l_dict = {}
    for row in nested_list:
        l_dict[row[1][key]] = row

    sorted_list = []
    for key in sort_nicely(l_dict):
        sorted_list.append(l_dict[key])

    return sorted_list

def has_duplicate_title(entries, this_entry, proposed_title):
    for entry in entries:
        if entry[0] != this_entry and entry[1]["title"] == proposed_title:
            return True
    return False

def save_course(course_basics, course_details):
    basics_to_save = {"id": course_basics["id"], "title": course_basics["title"], "visible": course_basics["visible"]}
    write_file(convert_dict_to_yaml(basics_to_save), get_course_dir_path(course_basics["id"]) + "basics")
    write_file(convert_dict_to_yaml(course_details), get_course_dir_path(course_basics["id"]) + "details")

def save_assignment(assignment_basics, assignment_details):
    basics_to_save = {"id": assignment_basics["id"], "title": assignment_basics["title"], "visible": assignment_basics["visible"]}
    write_file(convert_dict_to_yaml(basics_to_save), get_assignment_dir_path(assignment_basics["course"]["id"], assignment_basics["id"]) + "basics")
    write_file(convert_dict_to_yaml(assignment_details), get_assignment_dir_path(assignment_basics["course"]["id"], assignment_basics["id"]) + "details")

def save_problem(problem_basics, problem_details):
    if "data_urls" in problem_details:
        del problem_details["data_urls"]

    basics_to_save = {"id": problem_basics["id"], "title": problem_basics["title"], "visible": problem_basics["visible"]}
    write_file(convert_dict_to_yaml(basics_to_save), get_problem_dir_path(problem_basics["assignment"]["course"]["id"], problem_basics["assignment"]["id"], problem_basics["id"]) + "basics")
    write_file(convert_dict_to_yaml(problem_details), get_problem_dir_path(problem_basics["assignment"]["course"]["id"], problem_basics["assignment"]["id"], problem_basics["id"]) + "details")

def save_submission(course, assignment, problem, user, code, code_output, passed, date, error_occurred):
    submission_id = get_next_submission_id(course, assignment, problem, user)
    submission_dict = {"code": code, "code_output": code_output, "passed": passed, "date": date, "error_occurred": error_occurred}
    write_file(convert_dict_to_yaml(submission_dict), get_submission_file_path(course, assignment, problem, user, submission_id))

    return submission_id

def delete_problem(problem_basics):
    dir_path = get_problem_dir_path(problem_basics["assignment"]["course"]["id"], problem_basics["assignment"]["id"], problem_basics["id"])
    shutil.rmtree(dir_path, ignore_errors=True)
    shutil.rmtree(f"/submissions/{problem_basics['assignment']['course']['id']}/{problem_basics['assignment']['id']}/{problem_basics['id']}", ignore_errors=True)

def delete_assignment(assignment_basics):
    dir_path = get_assignment_dir_path(assignment_basics["course"]["id"], assignment_basics["id"])
    shutil.rmtree(dir_path, ignore_errors=True)
    shutil.rmtree(f"/submissions/{assignment_basics['course']['id']}/{assignment_basics['id']}", ignore_errors=True)

def delete_course(course_basics):
    shutil.rmtree(get_course_dir_path(course_basics["id"]), ignore_errors=True)
    shutil.rmtree(f"/submissions/{course_basics['id']}", ignore_errors=True)
