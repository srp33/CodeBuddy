from datetime import datetime
import glob
import gzip
from helper import *
import io
import json
import os
import re
import yaml
from yaml import load
from yaml import Loader
import zipfile
import sqlite3
from sqlite3 import Error
import atexit
import html

class Content:
    def __init__(self, settings_dict):
        self.__settings_dict = settings_dict

        # This enables auto-commit.
        self.conn = sqlite3.connect(settings_dict["db_location"], isolation_level=None, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor()
        self.c.execute("PRAGMA foreign_keys=ON")

        atexit.register(self.close)

    def close(self):
        self.c.close()
        self.conn.close()

    def create_sqlite_tables(self):
        create_users_table = '''CREATE TABLE IF NOT EXISTS users (
                                  user_id text PRIMARY KEY
                                );'''

        create_permissions_table = '''CREATE TABLE IF NOT EXISTS permissions (
                                        user_id text NOT NULL,
                                        role text NOT NULL,
                                        course_id text,
                                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                                        PRIMARY KEY (user_id)
                                      );'''

        create_courses_table = '''CREATE TABLE IF NOT EXISTS courses (
                                    course_id text NOT NULL,
                                    title text NOT NULL UNIQUE,
                                    introduction text,
                                    visible integer NOT NULL,
                                    date_created timestamp NOT NULL,
                                    date_updated timestamp NOT NULL,
                                    PRIMARY KEY (course_id)
                                  );'''

        create_assignments_table = '''CREATE TABLE IF NOT EXISTS assignments (
                                        course_id text NOT NULL,
                                        assignment_id text NOT NULL,
                                        title text NOT NULL UNIQUE,
                                        introduction text,
                                        visible integer NOT NULL,
                                        date_created timestamp NOT NULL,
                                        date_updated timestamp NOT NULL,
                                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE,
                                        PRIMARY KEY (assignment_id)
                                      );'''

        create_problems_table = '''CREATE TABLE IF NOT EXISTS problems (
                                     course_id text NOT NULL,
                                     assignment_id text NOT NULL,
                                     problem_id text NOT NULL,
                                     title text NOT NULL UNIQUE,
                                     visible integer NOT NULL,
                                     answer_code text NOT NULL,
                                     answer_description text,
                                     credit text,
                                     data_url text,
                                     data_file_name text,
                                     data_contents text,
                                     back_end text NOT NULL,
                                     expected_output text NOT NULL,
                                     instructions text NOT NULL,
                                     output_type text NOT NULL,
                                     show_answer integer NOT NULL,
                                     show_expected integer NOT NULL,
                                     show_test_code integer NOT NULL,
                                     test_code text,
                                     date_created timestamp NOT NULL,
                                     date_updated timestamp NOT NULL,
                                     FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE,
                                     FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE ON UPDATE CASCADE,
                                     PRIMARY KEY (problem_id)
                                   );'''

        create_submissions_table = '''CREATE TABLE IF NOT EXISTS submissions (
                                        course_id text NOT NULL,
                                        assignment_id text NOT NULL,
                                        problem_id text NOT NULL,
                                        user_id text NOT NULL,
                                        submission_id integer NOT NULL,
                                        code text NOT NULL,
                                        code_output text NOT NULL,
                                        passed integer NOT NULL,
                                        date timestamp NOT NULL,
                                        error_occurred integer NOT NULL,
                                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE,
                                        FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE,
                                        FOREIGN KEY (problem_id) REFERENCES problems (problem_id) ON DELETE CASCADE,
                                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                                        PRIMARY KEY (course_id, assignment_id, problem_id, user_id, submission_id)
                                      );'''

        if self.conn is not None:
            self.c.execute(create_users_table)
            self.c.execute(create_permissions_table)
            self.c.execute(create_courses_table)
            self.c.execute(create_assignments_table)
            self.c.execute(create_problems_table)
            self.c.execute(create_submissions_table)

            if len(self.get_courses()) == 0:
                for user_id in self.__settings_dict["initial_administrators"]:
                    if not self.check_user_exists(user_id):
                        self.add_user(user_id)
                    self.add_permissions(user_id, "administrator", None)
        else:
            print("Error! Cannot create the database connection.")

    def check_user_exists(self, user_id):
        sql = 'SELECT user_id FROM users WHERE user_id = ?'
        self.c.execute(sql, (user_id,))
        return self.c.fetchone() != None

    def get_role(self, user_id):
        sql = 'SELECT role FROM permissions WHERE user_id = ?'
        self.c.execute(sql, (str(user_id),))
        row = self.c.fetchone()

        if row:
            return row["role"]
        else:
            return "student"

    def get_users_from_role(self, role, course_id):
        sql = '''SELECT user_id
                 FROM permissions
                 WHERE role = ?
                 AND (course_id = ? OR course_id IS NULL)'''
        rows = self.c.execute(sql, (role, course_id,))
        return [row["user_id"] for row in rows]

    def add_user(self, user_id):
        sql = 'INSERT INTO users (user_id) VALUES (?)'
        self.c.execute(sql, (user_id,))

    def add_permissions(self, user_id, role, course_id):
        if not self.check_user_exists(user_id):
            return False

        sql = '''SELECT role
                 FROM permissions
                 WHERE user_id = ?
                   AND (course_id = ? OR course_id IS NULL)'''
        self.c.execute(sql, (user_id, course_id,))
        role_exists = self.c.fetchone() != None

        if role_exists:
            sql = '''UPDATE permissions
                     SET role = ?, course_id = ?
                     WHERE user_id = ?'''
            self.c.execute(sql, (role, course_id, user_id,))
        else:
            sql = '''INSERT INTO permissions (user_id, role, course_id)
                     VALUES (?, ?, ?)'''
            self.c.execute(sql, (user_id, role, course_id,))

        return True

    def get_course_ids(self):
        sql = 'SELECT course_id FROM courses'
        self.c.execute(sql)
        return [course[0] for course in self.c.fetchall()]

    def get_assignment_ids(self, course_id):
        sql = 'SELECT assignment_id FROM assignments WHERE course_id = ?'
        self.c.execute(sql, (str(course_id),))
        return [assignment[0] for assignment in self.c.fetchall()]

    def get_problem_ids(self, course_id, assignment_id):
        sql = 'SELECT problem_id FROM problems WHERE assignment_id = ?'
        self.c.execute(sql, (str(assignment_id),))
        return [problem[0] for problem in self.c.fetchall()]

    def get_courses(self, show_hidden=True):
        courses = []
        course_ids = self.get_course_ids()

        for course_id in course_ids:
            course_basics = self.get_course_basics(course_id)
            if course_basics["visible"] or show_hidden:
                courses.append([course_id, course_basics])

        return self.sort_nested_list(courses)

    def get_course_title_from_id(self, course_id, show_hidden=True):
        sql = 'SELECT title FROM courses WHERE course_id = ?'
        self.c.execute(sql, (str(course_id),))
        row = self.c.fetchone()
        return row["title"]

    def get_assignment_title_from_id(self, assignment_id, show_hidden=True):
        sql = 'SELECT title FROM assignments WHERE assignment_id = ?'
        self.c.execute(sql, (str(assignment_id),))
        row = self.c.fetchone()
        return row["title"]

    def get_assignments(self, course_id, show_hidden=True):
        assignments = []
        assignment_ids = self.get_assignment_ids(course_id)

        for assignment_id in assignment_ids:
            assignment_basics = self.get_assignment_basics(course_id, assignment_id)
            if assignment_basics["visible"] or show_hidden:
                assignments.append([assignment_id, assignment_basics])

        return self.sort_nested_list(assignments)

    def get_problems(self, course_id, assignment_id, show_hidden=True):
        problems = []
        problem_ids = self.get_problem_ids(course_id, assignment_id)

        for problem_id in problem_ids:
            problem_basics = self.get_problem_basics(course_id, assignment_id, problem_id)
            if problem_basics["visible"] or show_hidden:
                problems.append([problem_id, problem_basics, course_id, assignment_id])

        return self.sort_nested_list(problems)

    def get_problem_statuses(self, user_id, course_id, assignment_id, show_hidden=True):
        problem_statuses = []
        problem_dict = {"id": "", "title": "", "passed": 0}

        sql = '''SELECT p.problem_id, p.title, IFNULL(MAX(s.passed), 0) AS passed, COUNT(s.submission_id) AS num_attempts
                 FROM problems p
                 LEFT JOIN submissions s
                  ON p.problem_id = s.problem_id
                 WHERE p.assignment_id = ?
                  AND (s.user_id = ? OR s.user_id IS NULL)
                 GROUP BY p.assignment_id, p.problem_id
                 ORDER BY p.title'''
        self.c.execute(sql,(str(assignment_id), str(user_id),))
        for row in self.c.fetchall():
            problem_dict = {"id": row["problem_id"], "title": row["title"], "passed": row["passed"]}
            problem_statuses.append([row["problem_id"], problem_dict])

        return problem_statuses

    def get_submissions_basic(self, course_id, assignment_id, problem_id, user_id):
        submissions = []
        sql = '''SELECT submission_id, date, passed
                 FROM submissions
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND problem_id = ?
                   AND user_id = ?
                  ORDER BY submission_id DESC'''

        self.c.execute(sql, (str(course_id), str(assignment_id), str(problem_id), str(user_id),))

        for submission in self.c.fetchall():
            submissions.append([submission["submission_id"], submission["date"].strftime("%m/%d/%Y, %I:%M:%S %p"), submission["passed"]])

        return submissions

    def specify_course_basics(self, course_basics, title, visible):
        course_basics["title"] = title
        course_basics["visible"] = visible

    def specify_course_details(self, course_details, introduction, date_created, date_updated):
        course_details["introduction"] = introduction
        course_details["date_updated"] = date_updated

        if course_details["date_created"]:
            course_details["date_created"] = date_created
        else:
            course_details["date_created"] = date_updated

    def specify_assignment_basics(self, assignment_basics, title, visible):
        assignment_basics["title"] = title
        assignment_basics["visible"] = visible

    def specify_assignment_details(self, assignment_details, introduction, date_created, date_updated):
        assignment_details["introduction"] = introduction
        assignment_details["date_updated"] = date_updated

        if assignment_details["date_created"]:
            assignment_details["date_created"] = date_created
        else:
            assignment_details["date_created"] = date_updated

    def specify_problem_basics(self, problem_basics, title, visible):
        problem_basics["title"] = title
        problem_basics["visible"] = visible

    def specify_problem_details(self, problem_details, instructions, back_end, output_type, answer_code, answer_description, test_code, credit, data_url, data_file_name, data_contents, show_expected, show_test_code, show_answer, expected_output, date_created, date_updated):
        problem_details["instructions"] = instructions
        problem_details["back_end"] = back_end
        problem_details["output_type"] = output_type
        problem_details["answer_code"] = answer_code
        problem_details["answer_description"] = answer_description
        problem_details["test_code"] = test_code
        problem_details["credit"] = credit
        problem_details["data_url"] = data_url
        problem_details["data_file_name"] = data_file_name
        problem_details["data_contents"] = data_contents
        problem_details["show_expected"] = show_expected
        problem_details["show_test_code"] = show_test_code
        problem_details["show_answer"] = show_answer
        problem_details["expected_output"] = expected_output
        problem_details["date_updated"] = date_updated

        if problem_details["date_created"]:
            problem_details["date_created"] = date_created
        else:
            problem_details["date_created"] = date_updated

    def get_course_basics(self, course_id):
        if not course_id:
            course_id = create_id(self.get_courses())

        sql = '''SELECT course_id, title, visible
                 FROM courses
                 WHERE course_id = ?'''
        self.c.execute(sql, (str(course_id),))
        row = self.c.fetchone()

        if row is None:
            return {"id": course_id, "title": "", "visible": True, "exists": False}
        else:
            return {"id": row["course_id"], "title": row["title"], "visible": bool(row["visible"]), "exists": True}

    def get_assignment_basics(self, course_id, assignment_id):
        if not assignment_id:
            assignment_id = create_id(self.get_assignments(course_id))

        course_basics = self.get_course_basics(course_id)

        sql = '''SELECT assignment_id, title, visible
                 FROM assignments
                 WHERE assignment_id = ?'''
        self.c.execute(sql, (str(assignment_id),))
        row = self.c.fetchone()
        if row is None:
            return {"id": assignment_id, "title": "", "visible": True, "exists": False, "course": course_basics}
        else:
            return {"id": row["assignment_id"], "title": row["title"], "visible": bool(row["visible"]), "exists": True, "course": course_basics}

    def get_problem_basics(self, course_id, assignment_id, problem_id):
        if not problem_id:
            problem_id = create_id(self.get_problems(course_id, assignment_id))

        assignment_basics = self.get_assignment_basics(course_id, assignment_id)

        sql = '''SELECT problem_id, title, visible
                 FROM problems
                 WHERE problem_id = ?'''
        self.c.execute(sql, (str(problem_id),))
        row = self.c.fetchone()
        if row is None:
            return {"id": problem_id, "title": "", "visible": True, "exists": False, "assignment": assignment_basics}
        else:
            return {"id": row["problem_id"], "title": row["title"], "visible": bool(row["visible"]), "exists": True, "assignment": assignment_basics}

    def get_next_prev_problems(self, course, assignment, problem, problems):
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

    def get_num_submissions(self, course, assignment, problem, user):
        sql = '''SELECT COUNT(*)
                 FROM submissions
                 WHERE problem_id = ?
                  AND user_id = ?'''

        return self.c.execute(sql, (problem, user,)).fetchone()[0]

    def get_user_total_submissions(self, user):
        sql = 'SELECT COUNT(*) FROM submissions WHERE user_id = ?'
        num_submissions = self.c.execute(sql, (user,)).fetchone()[0]
        return num_submissions

    def get_next_submission_id(self, course, assignment, problem, user):
        return self.get_num_submissions(course, assignment, problem, user) + 1

    def get_last_submission(self, course, assignment, problem, user):
        last_submission_id = self.get_num_submissions(course, assignment, problem, user)
        sql = '''SELECT code, code_output, passed, date, error_occurred
                 FROM submissions
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND problem_id = ?
                   AND user_id = ?
                   AND submission_id = ?'''

        self.c.execute(sql, (course, assignment, problem, user, last_submission_id,))
        row = self.c.fetchone()

        return {"id": last_submission_id, "code": row["code"], "code_output": row["code_output"], "passed": row["passed"], "date": row["date"], "error_occurred": row["error_occurred"], "exists": True}

    def get_submission_info(self, course, assignment, problem, user, submission):
        sql = '''SELECT code, code_output, passed, date, error_occurred
                 FROM submissions
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND problem_id = ?
                   AND user_id = ?
                   AND submission_id = ?'''

        self.c.execute(sql, (course, assignment, problem, user, submission,))
        row = self.c.fetchone()

        return {"id": submission, "code": row["code"], "code_output": row["code_output"], "passed": row["passed"], "date": row["date"].strftime("%m/%d/%Y, %I:%M:%S %p"), "error_occurred": row["error_occurred"], "exists": True}

    def get_course_details(self, course, format_output=False):
        sql = '''SELECT introduction, date_created, date_updated
                 FROM courses
                 WHERE course_id = ?'''
        self.c.execute(sql, (course,))

        row = self.c.fetchone()
        if row is None:
            return {"introduction": "", "date_created": None, "date_updated": None}
        else:
            course_dict = {"introduction": row["introduction"], "date_created": row["date_created"], "date_updated": row["date_updated"]}
            if format_output:
                course_dict["introduction"] = convert_markdown_to_html(course_dict["introduction"])

            return course_dict

    def get_assignment_details(self, course, assignment, format_output=False):
        sql = '''SELECT introduction, date_created, date_updated
                 FROM assignments
                 WHERE course_id = ? AND assignment_id = ?'''
        self.c.execute(sql, (course, assignment,))

        row = self.c.fetchone()
        if row is None:
            return {"introduction": "", "date_created": None, "date_updated": None}
        else:
            assignment_dict = {"introduction": row["introduction"], "date_created": row["date_created"], "date_updated": row["date_updated"]}
            if format_output:
                assignment_dict["introduction"] = convert_markdown_to_html(assignment_dict["introduction"])

            return assignment_dict

    def get_problem_details(self, course, assignment, problem, format_content=False):
        sql = '''SELECT instructions, back_end, output_type, answer_code, answer_description, test_code, credit, show_expected, show_test_code, show_answer, expected_output, data_url, data_file_name, data_contents, date_created, date_updated
                 FROM problems
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND problem_id = ?'''

        self.c.execute(sql, (course, assignment, problem,))
        row = self.c.fetchone()

        if row is None:
            return {"instructions": "", "back_end": "python",
            "output_type": "txt", "answer_code": "", "answer_description": "", "test_code": "",
            "credit": "", "show_expected": True, "show_test_code": True, "show_answer": True,
            "expected_output": "", "data_url": "", "data_file_name": "", "data_contents": "",
            "date_created": None, "date_updated": None}
        else:
            problem_dict = {"instructions": row["instructions"], "back_end": row["back_end"], "output_type": row["output_type"], "answer_code": row["answer_code"], "answer_description": row["answer_description"], "test_code": row["test_code"], "credit": row["credit"], "show_expected": row["show_expected"], "show_test_code": row["show_test_code"], "show_answer": row["show_answer"], "expected_output": row["expected_output"], "data_url": row["data_url"], "data_file_name": row["data_file_name"], "data_contents": row["data_contents"], "date_created": row["date_created"], "date_updated": row["date_updated"]}

            if format_content:
                problem_dict["instructions"] = convert_markdown_to_html(problem_dict["instructions"])
                problem_dict["credit"] = convert_markdown_to_html(problem_dict["credit"])
                problem_dict["answer_description"] = convert_markdown_to_html(problem_dict["answer_description"])

            return problem_dict

    def course_ids_to_titles(self):
        course_dict = {}
        sql = 'SELECT course_id, title FROM courses'
        self.c.execute(sql)
        for course in self.c.fetchall():
            course_dict[course["course_id"]] = course["title"]
        return course_dict

    def assignment_ids_to_titles(self):
        assignment_dict = {}
        sql = 'SELECT assignment_id, title FROM assignments'
        self.c.execute(sql)
        for assignment in self.c.fetchall():
            assignment_dict[assignment["assignment_id"]] = assignment["title"]
        return assignment_dict

    def problem_ids_to_titles(self):
        problem_dict = {}
        sql = 'SELECT problem_id, title FROM problems'
        self.c.execute(sql)
        for problem in self.c.fetchall():
            problem_dict[problem["problem_id"]] = problem["title"]
        return problem_dict

    def get_student_courses(self, student_id):
        courses = []
        sql = '''SELECT courses.course_id, courses.title, submissions.user_id
                 FROM courses
                 INNER JOIN submissions ON courses.course_id = submissions.course_id
                 WHERE submissions.user_id = ?'''
        self.c.execute(sql, (str(student_id),))
        for course in self.c.fetchall():
            courses.append([course["title"], course["course_id"]])
        return courses

    def get_student_assignments(self, student_id):
        assignments = []
        sql = '''SELECT assignments.course_id, assignments.assignment_id, assignments.title
                 FROM assignments
                 INNER JOIN submissions ON assignments.assignment_id = submissions.assignment_id
                 WHERE submissions.user_id = ?'''
        self.c.execute(sql, (str(student_id),))
        for assignment in self.c.fetchall():
            assignments.append([assignment["title"], assignment["course_id"], assignment["assignment_id"]])
        return assignments

    def get_student_problem_status(self, problem_id, student_id):
        passed = False
        sql = '''SELECT passed
                 FROM submissions
                 WHERE problem_id = ? AND user_id = ?'''
        self.c.execute(sql, (problem_id, student_id,))
        for submission in self.c.fetchall():
            if submission["passed"]:
                passed = True
        return passed

    def get_student_problems(self, student_id):  #returns list of problems a certain student has made submissions for, also whether the student has passed the problem and number of submissions student has made
        problems = []
        sql = '''SELECT DISTINCT problems.course_id, problems.assignment_id, problems.problem_id, problems.title
                 FROM problems
                 INNER JOIN submissions ON problems.problem_id = submissions.problem_id
                 WHERE submissions.user_id = ?'''
        self.c.execute(sql, (str(student_id),))

        for problem in self.c.fetchall():
            problems.append([problem["title"], problem["course_id"], problem["assignment_id"], problem["problem_id"]])
        for problem in problems:
            num_submissions = self.get_num_submissions(problem[1], problem[2], problem[3], student_id)
            passed = self.get_student_problem_status(problem[3], student_id)
            problem.append(num_submissions)
            problem.append(passed)

        return problems

    def get_log_table_contents(self, file_path, year="No filter", month="No filter", day="No filter"):
        new_dict = {}
        line_num = 1
        with gzip.open(file_path) as read_file:
            header = read_file.readline()
            for line in read_file:
                line_items = line.decode().rstrip("\n").split("\t")
                line_items = [line_items[0][:2], line_items[0][2:4], line_items[0][4:6], line_items[0][6:]] + line_items[1:]

                new_dict[line_num] = line_items
                line_num += 1

        # Filter by date.
        year_dict = {}
        month_dict = {}
        day_dict = {}

        for key, line in new_dict.items():
            if year == "No filter" or line[0] == year:
                year_dict[key] = line
        for key, line in year_dict.items():
            if month == "No filter" or line[1] == month:
                month_dict[key] = line
        for key, line in month_dict.items():
            if day == "No filter" or line[2] == day:
                day_dict[key] = line

        return day_dict

    def get_root_dirs_to_log(self):
        root_dirs_to_log = set(["home", "course", "assignment", "problem", "check_problem", "edit_course", "edit_assignment", "edit_problem", "delete_course", "delete_assignment", "delete_problem", "view_answer", "import_course", "export_course"])
        return root_dirs_to_log

    def sort_nested_list(self, nested_list, key="title"):
        l_dict = {}
        for row in nested_list:
            l_dict[row[1][key]] = row

        return [l_dict[key] for key in sort_nicely(l_dict)]

    def has_duplicate_title(self, entries, this_entry, proposed_title):
        for entry in entries:
            if entry[0] != this_entry and entry[1]["title"] == proposed_title:
                return True
        return False

    def save_course(self, course_basics, course_details):
        if course_basics["exists"]:
            sql = '''UPDATE courses
                     SET title = ?, visible = ?, introduction = ?, date_updated = ?
                     WHERE course_id = ?'''
            self.c.execute(sql, [course_basics["title"], course_basics["visible"], course_details["introduction"], course_details["date_updated"], course_basics["id"]])
        else:
            sql = '''INSERT INTO courses (course_id, title, visible, introduction, date_created, date_updated)
                     VALUES (?, ?, ?, ?, ?, ?)'''
            self.c.execute(sql, [course_basics["id"], course_basics["title"], course_basics["visible"], course_details["introduction"], course_details["date_created"], course_details["date_updated"]])
            course_basics["exists"] = True

    def save_assignment(self, assignment_basics, assignment_details):
        if assignment_basics["exists"]:
            sql = '''UPDATE assignments
                     SET title = ?, visible = ?, introduction = ?, date_updated = ?
                     WHERE course_id = ? AND assignment_id = ?'''
            self.c.execute(sql, [assignment_basics["title"], assignment_basics["visible"], assignment_details["introduction"], assignment_details["date_updated"], assignment_basics["course"]["id"], assignment_basics["id"]])
        else:
            sql = '''INSERT INTO assignments (course_id, assignment_id, title, visible, introduction, date_created, date_updated)
                     VALUES (?, ?, ?, ?, ?, ?, ?)'''
            self.c.execute(sql, [assignment_basics["course"]["id"], assignment_basics["id"], assignment_basics["title"], assignment_basics["visible"], assignment_details["introduction"], assignment_details["date_created"], assignment_details["date_updated"]])
            assignment_basics["exists"] = True

    def save_problem(self, problem_basics, problem_details):
        if problem_basics["exists"]:
            sql = '''UPDATE problems
                     SET title = ?, visible = ?,
                         answer_code = ?, answer_description = ?, credit = ?, data_url = ?, data_file_name = ?,
                         data_contents = ?, back_end = ?, expected_output = ?, instructions = ?,
                         output_type = ?, show_answer = ?, show_expected = ?, show_test_code = ?, test_code = ?, date_updated = ?
                     WHERE course_id = ? AND assignment_id = ? AND problem_id = ?'''
            self.c.execute(sql, [problem_basics["title"], problem_basics["visible"], str(problem_details["answer_code"]), problem_details["answer_description"], problem_details["credit"], problem_details["data_url"], problem_details["data_file_name"], problem_details["data_contents"], problem_details["back_end"], problem_details["expected_output"], problem_details["instructions"], problem_details["output_type"], problem_details["show_answer"], problem_details["show_expected"], problem_details["show_test_code"], problem_details["test_code"], problem_details["date_updated"], problem_basics["assignment"]["course"]["id"], problem_basics["assignment"]["id"], problem_basics["id"]])
        else:
            sql = '''INSERT INTO problems (course_id, assignment_id, problem_id, title, visible, answer_code, answer_description, credit, data_url, data_file_name, data_contents, back_end, expected_output, instructions, output_type, show_answer, show_expected, show_test_code, test_code, date_created, date_updated)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
            self.c.execute(sql, [problem_basics["assignment"]["course"]["id"], problem_basics["assignment"]["id"], problem_basics["id"], problem_basics["title"], problem_basics["visible"], str(problem_details["answer_code"]), problem_details["answer_description"], problem_details["credit"], problem_details["data_url"], problem_details["data_file_name"], problem_details["data_contents"], problem_details["back_end"], problem_details["expected_output"], problem_details["instructions"], problem_details["output_type"], problem_details["show_answer"], problem_details["show_expected"], problem_details["show_test_code"], problem_details["test_code"], problem_details["date_created"], problem_details["date_updated"]])

    def save_submission(self, course, assignment, problem, user, code, code_output, passed, error_occurred):
        submission_id = self.get_next_submission_id(course, assignment, problem, user)
        sql = ''' INSERT INTO submissions (course_id, assignment_id, problem_id, user_id, submission_id, code, code_output, passed, date, error_occurred)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        self.c.execute(sql, [course, assignment, problem, user, submission_id, code, code_output, passed, datetime.now(), error_occurred])

        return submission_id

    def update_user(self, old_id, new_id):
        sql = 'UPDATE users SET user_id = ? WHERE user_id'
        self.c.execute(sql, (new_id, old_id,))

    def update_role(self, user_id, new_role):
        sql = 'UPDATE users SET role = ? WHERE user_id = ?'
        self.c.execute(sql, (new_role, user_id,))

    def delete_rows_with_value(self, table, col_name, value):
        sql = 'DELETE FROM ' + table + ' WHERE ' + col_name + ' = ?'
        self.c.execute(sql, (value,))

    def delete_all_rows(self, table):
        sql = 'DELETE FROM ' + table
        self.c.execute(sql)

    def delete_problem(self, problem_basics):
        self.delete_rows_with_value("problems", "problem_id", problem_basics["id"])
        self.delete_problem_submissions(problem_basics)

    def delete_assignment(self, assignment_basics):
        self.delete_rows_with_value("assignments", "assignment_id", assignment_basics["id"])
        self.delete_assignment_submissions(assignment_basics)

    def delete_course(self, course_basics):
        self.delete_rows_with_value("courses", "course_id", course_basics["id"])
        self.delete_course_submissions(course_basics)

    def delete_course_submissions(self, course_basics):
        self.delete_rows_with_value("submissions", "course_id", course_basics["id"])

    def delete_assignment_submissions(self, assignment_basics):
        self.delete_rows_with_value("submissions", "assignment_id", assignment_basics["id"])

    def delete_problem_submissions(self, problem_basics):
        self.delete_rows_with_value("submissions", "problem_id", problem_basics["id"])

    def export_course(self, course_basics, table_name, output_tsv_file_path):
        sql = f"SELECT * FROM {table_name} WHERE course_id = ?"
        self.c.execute(sql, (course_basics["id"],))

        rows = []
        for row in self.c.fetchall():
            row_values = []
            for x in row:
                if type(x) is datetime:
                    x = str(x)
                row_values.append(x)

            rows.append(row_values)

        with open(output_tsv_file_path, "w") as out_file:
            out_file.write(json.dumps(rows))
