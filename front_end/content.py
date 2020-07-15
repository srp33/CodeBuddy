import glob
from helper import *
import io
import os
import yaml
from yaml import load
from yaml import Loader
import zipfile
import sqlite3
from sqlite3 import Error
import atexit

def get_environments():
    return load_yaml_dict(read_file("/Environments.yaml"))

def create_sqlite_connection():
    conn = None
    try:
        conn = sqlite3.connect(r"/submissions/test.db")
        print("SQLite connection established")
        return conn
    except Error as e:
        print(e)
    return conn

def close_sqlite_connection(conn):
    conn.close()
    print("The SQLite connection is closed")

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def print_tables(conn):
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    #print(c.fetchall())
    for row in c.fetchall():
        print(row)

def print_rows(conn, table):
    c = conn.cursor()
    c.execute(''' SELECT * FROM ''' + table + ''';''')
    rows = c.fetchall()
    for row in rows:
        print(row)

def delete_row_with_attribute(conn, row_name, row_value, table):
    sql = 'DELETE FROM ' + table + ' WHERE ' + row_name + '=?'
    c = conn.cursor()
    c.execute(sql, (row_value,))
    conn.commit()

def delete_col(conn, table, cols_to_keep): #only works if not deleting primary key, works for multiple rows I think
    cur = conn.cursor()

    sql_new_table_cols = ""
    new_col_list = ""

    for col in cols_to_keep:
        if row == cols_to_keep[0]:
            sql_new_table_cols += col + " text PRIMARY KEY, "
            new_col_list += col + ", "
        elif col == cols_to_keep[-1]:
            sql_new_table_cols += col + " text NOT NULL"
            new_col_list += col
        else:
            sql_new_table_cols += col + " text NOT NULL, "
            new_col_list += col + ", "

    sql = """ PRAGMA foreign_keys=off;
                BEGIN TRANSACTION;

                CREATE TABLE IF NOT EXISTS new_table (""" + sql_new_table_cols + """);

                INSERT INTO new_table(""" + new_col_list + """)
                SELECT """ + new_col_list + """
                FROM """ + table + """;

                DROP TABLE """ + table + """;

                ALTER TABLE new_table RENAME TO """ + table + """; 

                COMMIT;

                PRAGMA foreign_keys=on; """

    #cur.execute() #need to have a separate execute statement for each sqlite command

    cur.execute(sql)

def delete_all_rows(conn, table):
    sql = 'DELETE FROM ' + table
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()

def delete_table(conn, table):
    sql = 'DROP TABLE ' + table
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()

def add_row(conn, table, col_list, row_info): #only works if there are 3 columns :/
    sql = ''' INSERT INTO ''' + table + ''' (''' + col_list + ''')
              VALUES(?,?,?) '''
    cur = conn.cursor()
    row = (row_info)
    cur.execute(sql, row)
    conn.commit()
    return cur.lastrowid

def add_row_user_info(conn, user_id):
    c = conn.cursor()
    c.execute(''' INSERT INTO user_info (user_id) VALUES (?)''', [user_id])
    conn.commit()

def add_row_permissions(conn, user_id, role):
    c = conn.cursor()
    c.execute(''' INSERT INTO permissions (user_id, role) VALUES (?, ?)''', [user_id, role])
    conn.commit()

def add_row_courses(conn, course_id, title, visible, introduction):
    c = conn.cursor()
    c.execute(''' INSERT INTO courses (course_id, title, visible, introduction) VALUES (?, ?, ?, ?)''', [course_id, title, visible, introduction])
    conn.commit()

def add_row_assignments(conn, course_id, assignment_id, title, visible, introduction):
    c = conn.cursor()
    c.execute(''' INSERT INTO courses (course_id, assignment_id, title, visible, introduction) VALUES (?, ?, ?, ?, ?)''', [course_id, assignment_id, title, visible, introduction])
    conn.commit()

def add_row_problems(conn, course_id, assignment_id, problem_id, title, visible, answer_code, answer_description, credit, data_urls_info, environment, expected_output, instructions, output_type, show_answer, show_expected, show_test_code, test_code):
    c = conn.cursor()
    c.execute(''' INSERT INTO courses (course_id, assignment_id, title, visible, introduction) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', [course_id, assignment_id, problem_id, title, visible, answer_code, answer_description, credit, data_urls_info, environment, expected_output, instructions, output_type, show_answer, show_expected, show_test_code, test_code])
    conn.commit()

def add_row_submissions(conn, course_id, assignment_id, problem_id, user_id, submission_id, code, code_output, passed, date, error_occurred):
    c = conn.cursor()
    c.execute(''' INSERT INTO submissions (course_id, assignment_id, problem_id, user_id, submission_id, code, code_output, passed, date, error_occurred) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', [course_id, assignment_id, problem_id, user_id, submission_id, code, code_output, passed, date, error_occurred])
    conn.commit()

def create_sqlite_tables(conn): #make id's integers?
    create_user_info_table = """ CREATE TABLE IF NOT EXISTS user_info (
                                        user_id text PRIMARY KEY
                                    ); """

    create_permissions_table = """ CREATE TABLE IF NOT EXISTS permissions (
                                        user_id	text NOT NULL, 
                                        role text NOT NULL,
                                        FOREIGN KEY (user_id) REFERENCES user_info (user_id),
                                        PRIMARY KEY (user_id)
                                    ); """

    create_courses_table = """ CREATE TABLE IF NOT EXISTS courses (
                                    course_id text NOT NULL,
                                    title text NOT NULL,
                                    visible integer NOT NULL,
                                    introduction text,
                                    PRIMARY KEY (course_id)
                                ); """

    create_assignments_table = """ CREATE TABLE IF NOT EXISTS assignments (
                                        course_id text NOT NULL,
                                        assignment_id text NOT NULL,
                                        title text NOT NULL,
                                        visible integer NOT NULL,
                                        introduction text,
                                        FOREIGN KEY (course_id) REFERENCES courses (course_id),
                                        PRIMARY KEY (assignment_id)
                                    ); """

    create_problems_table = """ CREATE TABLE IF NOT EXISTS problems (
                                    course_id text NOT NULL,
                                    assignment_id text NOT NULL,
                                    problem_id text NOT NULL,
                                    title text NOT NULL,
                                    visible integer NOT NULL,
                                    answer_code text NOT NULL,
                                    answer_description text,
                                    credit text,
                                    data_urls_info text,
                                    environment text NOT NULL,
                                    expected_output text NOT NULL,
                                    instructions text NOT NULL,
                                    output_type text NOT NULL,
                                    show_answer integer NOT NULL,
                                    show_expected integer NOT NULL,
                                    show_test_code integer NOT NULL,
                                    test_code text,
                                    FOREIGN KEY (course_id) REFERENCES courses (course_id),
                                    FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id),
                                    PRIMARY KEY (problem_id)
                                ); """

    create_submissions_table = """ CREATE TABLE IF NOT EXISTS submissions (
                                        course_id text NOT NULL,
                                        assignment_id text NOT NULL,
                                        problem_id text NOT NULL,
                                        user_id text NOT NULL,
                                        submission_id integer NOT NULL,
                                        code text NOT NULL,
                                        code_output text NOT NULL,
                                        passed integer NOT NULL,
                                        date text NOT NULL,
                                        error_occurred integer NOT NULL,
                                        FOREIGN KEY (user_id) REFERENCES user_info(user_id),
                                        PRIMARY KEY (course_id, assignment_id, problem_id, user_id, submission_id)
                                    ); """

    # create a database connection
    #conn = create_sqlite_connection()

    # create tables
    if conn is not None:
        create_table(conn, create_user_info_table)
        create_table(conn, create_permissions_table)
        create_table(conn, create_courses_table)
        create_table(conn, create_assignments_table)
        create_table(conn, create_problems_table)
        create_table(conn, create_submissions_table)

        #add_row_user_info(conn, "ajohns58")
        #add_row_permissions(conn, "ajohns58", "student")
        print_rows(conn, "user_info")
        print_rows(conn, "permissions")
        
        print_tables(conn)

    else:
        print("Error! Cannot create the database connection.")
    
    #close_sqlite_connection(conn)

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

    return sorted(submissions, key = lambda x: x[0])

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
    num_submissions = 0
    for submission in glob.glob(get_submission_dir_path(course, assignment, problem, user)):
        num_submissions += 1
    return num_submissions + 1

def get_last_submission(course, assignment, problem, user):
    last_submission_id = get_next_submission_id(course, assignment, problem, user) - 1
    file_path = f"/submissions/{course}/{assignment}/{problem}/{user}/{last_submission_id}.yaml"
    last_submission = load_yaml_dict(read_file(file_path))

    return last_submission

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

    conn = create_sqlite_connection()
    add_row_courses(conn, course_basics["id"], course_basics["title"], course_basics["visible"], course_details["introduction"])
    print_rows(conn, "courses")
    close_sqlite_connection(conn)

def save_assignment(assignment_basics, assignment_details):
    basics_to_save = {"id": assignment_basics["id"], "title": assignment_basics["title"], "visible": assignment_basics["visible"]}
    write_file(convert_dict_to_yaml(basics_to_save), get_assignment_dir_path(assignment_basics["course"]["id"], assignment_basics["id"]) + "basics")
    write_file(convert_dict_to_yaml(assignment_details), get_assignment_dir_path(assignment_basics["course"]["id"], assignment_basics["id"]) + "details")

    conn = create_sqlite_connection()
    add_row_assignments(conn, assignment_basics["course"]["id"], assignment_basics["id"], assignment_basics["title"], assignment_basics["visible"], assignment_details["introduction"])
    print_rows(conn, "assignments")
    close_sqlite_connection(conn)

def save_problem(problem_basics, problem_details):
    if "data_urls" in problem_details:
        del problem_details["data_urls"]

    basics_to_save = {"id": problem_basics["id"], "title": problem_basics["title"], "visible": problem_basics["visible"]}
    write_file(convert_dict_to_yaml(basics_to_save), get_problem_dir_path(problem_basics["assignment"]["course"]["id"], problem_basics["assignment"]["id"], problem_basics["id"]) + "basics")
    write_file(convert_dict_to_yaml(problem_details), get_problem_dir_path(problem_basics["assignment"]["course"]["id"], problem_basics["assignment"]["id"], problem_basics["id"]) + "details")

    conn = create_sqlite_connection()
    add_row_problems(conn, problem_basics["assignment"]["course"]["id"], problem_basics["assignment"]["id"], problem_basics["id"], problem_basics["title"], problem_basics["visible"], problem_details["answer_code"], problem_details["answer_description"], problem_details["credit"], problem_details["data_urls_info"], problem_details["environment"], problem_details["expected_output"], problem_details["instructions"], problem_details["output_type"], problem_details["show_answer"], problem_details["show_expected"], problem_details["show_test_code"], problem_details["test_code"])
    print_rows(conn, "problems")
    close_sqlite_connection(conn)

def save_submission(course, assignment, problem, user, code, code_output, passed, date, error_occurred):
    submission_id = get_next_submission_id(course, assignment, problem, user)
    submission_dict = {"code": code, "code_output": code_output, "passed": passed, "date": date, "error_occurred": error_occurred}
    write_file(convert_dict_to_yaml(submission_dict), get_submission_file_path(course, assignment, problem, user, submission_id))

    conn = create_sqlite_connection()
    add_row_submissions(conn, course, assignment, problem, user, submission_id, code, code_output, passed, date, error_occurred)
    print_rows(conn, "submissions")
    close_sqlite_connection(conn)

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
