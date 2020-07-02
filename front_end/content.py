import glob
from helper import *
import io
import os
import re
import yaml
from yaml import load
from yaml import Loader
import zipfile

def get_environments():
    return load_yaml_dict(read_file("/Environments.yaml"))

def get_administrators():
    return load_yaml_dict(read_file("/Administrators.yaml"))

def get_instructors():
    return load_yaml_dict(read_file("/Instructors.yaml"))

def get_root_dir_path():
    return "/course"

def get_course_ids():
    return [os.path.basename(x) for x in glob.glob("{}/*".format(get_root_dir_path()))]

def get_assignment_ids(course_id):
    assignment_ids = []
    for assignment_dir_path in glob.glob(get_course_dir_path(course_id) + "*"):
        if os.path.isdir(assignment_dir_path):
            assignment_ids.append(os.path.basename(assignment_dir_path))
    return assignment_ids

def get_problem_ids(course_id, assignment_id):
    problem_ids = []
    for problem_dir_path in glob.glob(get_root_dir_path() + f"/{course_id}/{assignment_id}/*"):
        if os.path.isdir(problem_dir_path):
            problem_ids.append(os.path.basename(problem_dir_path))
    return problem_ids


def get_courses(show_hidden=True):
    courses = []
    for course_id in get_course_ids():
        course_basics = get_course_basics(course_id)
        if course_basics["visible"] or show_hidden:
            courses.append([course_id, course_basics])

    return sort_by_title(courses)   

def get_assignments(course_id, show_hidden=True):
    assignments = []
    for assignment_id in get_assignment_ids(course_id):
        assignment_basics = get_assignment_basics(course_id, assignment_id)
        if assignment_basics["visible"] or show_hidden:
            assignments.append([assignment_id, assignment_basics])

    return sort_by_title(assignments)

def get_problems(course_id, assignment_id, show_hidden=True):
    problems = []

    for problem_id in get_problem_ids(course_id, assignment_id):
        problem_basics = get_problem_basics(course_id, assignment_id, problem_id)
        if problem_basics["visible"] or show_hidden:
            problems.append([problem_id, problem_basics])

    return sort_by_title(problems)

def get_course_dir_path(course):
    return get_root_dir_path() + f"/{course}/"

def get_assignment_dir_path(course, assignment):
    return get_root_dir_path() + f"/{course}/{assignment}/"

def get_problem_dir_path(course, assignment, problem):
    return get_root_dir_path() + f"/{course}/{assignment}/{problem}/"

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

def get_problem_details(course, assignment, problem, format_content=False, format_expected_output=False, parse_data_urls=False):
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

        if format_expected_output and problem_dict["output_type"] == "jpeg":
            problem_dict["expected_output"] = encode_image_bytes(problem_dict["expected_output"])

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

def get_titles(file_path):
    new_path = ""
    re_match = re.match(r"^\/(?P<name>[^\/]*)\/(?P<course_id>[^\/]*)\/?(?P<assignment_id>[^\/]*)\/?(?P<problem_id>[^\/]*)", file_path)
    if re_match:
        id_dict = re_match.groupdict()
        #for key, value in id_dict.items():
            #print (key)
            #print (value)

        course_title = ""
        assignment_title = ""
        problem_title = ""
    
        #courses = get_courses()
        #for course in courses:
        for course_id in get_course_ids():
            #print (course)
            course_basics = get_course_basics(course_id)
            #print (course_basics)
            if id_dict["course_id"] == course_id:
                course_title = course_basics["title"]

            for assignment_id in get_assignment_ids(course_id):
                assignment_basics = get_assignment_basics(course_id, assignment_id)
                if id_dict["assignment_id"] == assignment_id:
                    assignment_title = assignment_basics["title"]

                for problem_id in get_problem_ids(course_id, assignment_id):
                    problem_basics = get_problem_basics(course_id, assignment_id, problem_id)
                    if id_dict["problem_id"] == problem_id:
                        problem_title = problem_basics["title"]
      
        new_path = id_dict["name"]
        if course_title != "":
            new_path += "/" + course_title
            if assignment_title != "":
                new_path += "/" + assignment_title
                if problem_title != "":
                    new_path += "/" + problem_title

    return new_path

def sort_by_title(nested_list):
    l_dict = {}
    for row in nested_list:
        l_dict[row[1]["title"]] = row

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

def delete_problem(problem_basics):
    dir_path = get_problem_dir_path(problem_basics["assignment"]["course"]["id"], problem_basics["assignment"]["id"], problem_basics["id"])
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

def delete_assignment(assignment_basics):
    dir_path = get_assignment_dir_path(assignment_basics["course"]["id"], assignment_basics["id"])
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

def delete_course(course_basics):
    dir_path = get_course_dir_path(course_basics["id"])
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
