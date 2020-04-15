import glob
from helper import *
import os
import yaml
from yaml import load
from yaml import Loader

def get_environments():
    return load_yaml_dict(read_file("/Environments.yaml"))

def get_course_dir_path(course):
    return f"/course/{course}/"

def get_assignment_dir_path(course, assignment):
    return f"/course/{course}/{assignment}/"

def get_problem_dir_path(course, assignment, problem):
    return f"/course/{course}/{assignment}/{problem}/"

def get_course_basics(course, get_assignments=True):
    if not course:
        course = create_id()

    file_path = get_course_dir_path(course) + "basics"
    exists = os.path.exists(file_path)
    course_dict = {"id": course, "title": "", "exists": exists, "assignments": []}

    if exists:
        course_dict["title"] = read_file(file_path)

        if get_assignments:
            for assignment_dir_path in glob.glob(get_course_dir_path(course) + "*"):
                if os.path.isdir(assignment_dir_path):
                    assignment_id = os.path.basename(assignment_dir_path)
                    course_dict["assignments"].append([assignment_id, get_assignment_basics(course, assignment_id)])
            course_dict["assignments"] = sort_by_title(course_dict["assignments"])

    return course_dict

def get_assignment_basics(course, assignment, get_problems=True):
    if not assignment:
        assignment = create_id()

    file_path = get_assignment_dir_path(course, assignment) + "basics"
    exists = os.path.exists(file_path)
    assignment_dict = {"id": assignment, "title": "", "exists": exists, "course": get_course_basics(course, False), "problems": []}

    if exists:
        assignment_dict["title"] = read_file(file_path)

        if get_problems:
            for problem_dir_path in glob.glob(f"/course/{course}/{assignment}/*"):
                if os.path.isdir(problem_dir_path):
                    assignment_id = os.path.basename(problem_dir_path)
                    assignment_dict["problems"].append([problem_id, get_problem_basics(problem_id)])
            assignment_dict["problems"] = sort_by_title(assignment_dict["problems"])

    return assignment_dict

def get_problem_basics(course, assignment, problem):
    if not problem:
        problem = create_id()

    file_path = get_problem_dir_path(course, assignment, problem) + "basics"
    exists = os.path.exists(file_path)
    problem_dict = {"title": "", "exists": exists, "assignment": get_assignment_basics(course, assignment, False)}

    if exists:
        problem_dict["title"] = read_file(file_path)
        problem_dict["prev_problem"] = get_prev_problem(problem, problem_dict["assignment"]["problems"])
        problem_dict["next_problem"] = get_next_problem(problem, problem_dict["assignment"]["problems"])

    return problem_dict

def get_prev_problem(problem, assignment_problems):
    if len(assignment_problems) < 2 or problem == assignment_problems[0][0]:
        return None

    return assignment_problems[int(problem) - 2][0]

def get_next_problem(problem, assignment_problems):
    if len(assignment_problems) < 2 or problem == assignment_problems[-1][0]:
        return None

    return assignment_problems[int(problem)][0]

def get_courses():
    course_ids = [os.path.basename(x) for x in glob.glob("/course/*")]

    courses = []
    for course_id in course_ids:
        courses.append([course_id, get_course_basics(course_id, False)])

    return sort_by_title(courses)

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

def get_problem_details(course, assignment, problem, format_output=False):
    file_path = get_problem_dir_path(course, assignment, problem) + "details"

    if os.path.exists(file_path):
        problem_dict = load_yaml_dict(read_file(file_path))
    else:
        problem_dict = {"instructions": "", "environment": "r_codechecker",
            "output_type": "txt", "answer_code": "", "test_code": "", "credit": "",
            "data_urls": "", "show_expected": True, "show_test_code": True}

    return problem_dict

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
        if entry[0] != this_entry and  entry[1]["title"] == proposed_title:
            return True
    return False

def save_course(course_basics, course_details):
    write_file(course_basics["title"], get_course_dir_path(course_basics["id"]) + "basics")
    write_file(convert_dict_to_yaml(course_details), get_course_dir_path(course_basics["id"]) + "details")

def save_assignment(assignment_basics, assignment_details):
    write_file(assignment_basics["title"], get_assignment_dir_path(assignment_basics["course"]["id"], assignment_basics["id"]) + "basics")
    write_file(convert_dict_to_yaml(assignment_details), get_assignment_dir_path(assignment_basics["course"]["id"], assignment_basics["id"]) + "details")
