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
        self.conn = sqlite3.connect(f"/database/{settings_dict['db_name']}", isolation_level=None, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor()
        self.c.execute("PRAGMA foreign_keys=ON")

        atexit.register(self.close)

    def close(self):
        self.c.close()
        self.conn.close()

    def create_sqlite_tables(self):
        create_users_table = '''CREATE TABLE IF NOT EXISTS users (
                                  user_id text PRIMARY KEY,
                                  user_json text
                                );'''

        create_permissions_table = '''CREATE TABLE IF NOT EXISTS permissions (
                                        user_id text NOT NULL,
                                        role text NOT NULL,
                                        course_id integer,
                                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                                        PRIMARY KEY (user_id)
                                      );'''

        create_courses_table = '''CREATE TABLE IF NOT EXISTS courses (
                                    course_id integer PRIMARY KEY AUTOINCREMENT,
                                    title text NOT NULL UNIQUE,
                                    introduction text,
                                    visible integer NOT NULL,
                                    date_created timestamp NOT NULL,
                                    date_updated timestamp NOT NULL
                                  );'''

        create_assignments_table = '''CREATE TABLE IF NOT EXISTS assignments (
                                        course_id integer NOT NULL,
                                        assignment_id integer PRIMARY KEY AUTOINCREMENT,
                                        title text NOT NULL UNIQUE,
                                        introduction text,
                                        visible integer NOT NULL,
                                        date_created timestamp NOT NULL,
                                        date_updated timestamp NOT NULL,
                                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE
                                      );'''

        create_problems_table = '''CREATE TABLE IF NOT EXISTS problems (
                                     course_id integer NOT NULL,
                                     assignment_id integer NOT NULL,
                                     problem_id integer PRIMARY KEY AUTOINCREMENT,
                                     title text NOT NULL UNIQUE,
                                     visible integer NOT NULL,
                                     answer_code text NOT NULL,
                                     answer_description text,
                                     max_submissions integer NOT NULL,
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
                                     FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE ON UPDATE CASCADE
                                   );'''

        create_submissions_table = '''CREATE TABLE IF NOT EXISTS submissions (
                                        course_id integer NOT NULL,
                                        assignment_id integer NOT NULL,
                                        problem_id integer NOT NULL,
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
        else:
            print("Error! Cannot create a database connection.")

    def create_scores_text(self, course_id, assignment_id):
        out_file_text = "Course_ID,Assignment_ID,Student_ID,Score\n"
        scores = self.get_assignment_scores(course_id, assignment_id)

        for student in scores:
            out_file_text += f"{course_id},{assignment_id},{student[0]},{student[1]['percent_passed']}\n"

        return out_file_text

    def check_user_exists(self, user_id):
        sql = '''SELECT user_id
                 FROM users
                 WHERE user_id = ?'''

        self.c.execute(sql, (user_id,))
        return self.c.fetchone() != None

    def check_administrator_exists(self):
        sql = '''SELECT COUNT(*) AS num_administrators
                 FROM permissions
                 WHERE role = "administrator"'''

        self.c.execute(sql)
        return self.c.fetchone()["num_administrators"]

    def get_role(self, user_id):
        sql = '''SELECT role
                 FROM permissions
                 WHERE user_id = ?'''

        self.c.execute(sql, (user_id,))
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

    def add_user(self, user_id, user_dict):
        sql = '''INSERT INTO users (user_id, user_json)
                 VALUES (?, ?)'''

        self.c.execute(sql, (user_id, json.dumps(user_dict)))

    def add_permissions(self, user_id, role, course_id):
        sql = '''SELECT role
                 FROM permissions
                 WHERE user_id = ?
                   AND (course_id = ? OR course_id IS NULL)'''

        # Admins are not assigned to a particular course.
        if not course_id:
            course_id = "0"

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

    def add_admin_permissions(self, user_id):
        self.add_permissions(user_id, "administrator", None)

    def get_user_count(self):
        sql = '''SELECT COUNT(*) AS count
                 FROM users'''

        self.c.execute(sql)
        return self.c.fetchone()["count"]

    def get_course_ids(self):
        sql = '''SELECT course_id
                 FROM courses'''

        self.c.execute(sql)
        return [course[0] for course in self.c.fetchall()]

    def get_assignment_ids(self, course_id):
        if not course_id:
            return []

        sql = '''SELECT assignment_id
                 FROM assignments
                 WHERE course_id = ?'''

        self.c.execute(sql, (course_id,))
        return [assignment[0] for assignment in self.c.fetchall()]

    def get_problem_ids(self, course_id, assignment_id):
        if not assignment_id:
            return []

        sql = '''SELECT problem_id
                 FROM problems
                 WHERE assignment_id = ?'''

        self.c.execute(sql, (assignment_id,))
        return [problem[0] for problem in self.c.fetchall()]

    def get_courses(self, show_hidden=True):
        courses = []

        sql = '''SELECT course_id, title, visible
                 FROM courses
                 ORDER BY title'''
        self.c.execute(sql)

        for course in self.c.fetchall():
            if course["visible"] or show_hidden:
                course_basics = {"id": course["course_id"], "title": course["title"], "visible": course["visible"], "exists": True}
                courses.append([course["course_id"], course_basics])

        return courses

    def get_assignments(self, course_id, show_hidden=True):
        assignments = []

        sql = '''SELECT assignment_id, title, visible
                 FROM assignments
                 WHERE course_id = ?
                 ORDER BY title'''
        self.c.execute(sql, (str(course_id),))

        for assignment in self.c.fetchall():
            if assignment["visible"] or show_hidden:
                course_basics = self.get_course_basics(course_id)
                assignment_basics = {"id": assignment["assignment_id"], "title": assignment["title"], "visible": assignment["visible"], "exists": False, "course": course_basics}
                assignments.append([assignment["assignment_id"], assignment_basics])

        return assignments

    def get_problems(self, course_id, assignment_id, show_hidden=True):
        problems = []

        sql = '''SELECT problem_id, title, visible
                 FROM problems
                 WHERE course_id = ?
                 AND assignment_id = ?
                 ORDER BY title'''
        self.c.execute(sql, (str(course_id), str(assignment_id),))

        for problem in self.c.fetchall():
            if problem["visible"] or show_hidden:
                assignment_basics = self.get_assignment_basics(course_id, assignment_id)
                problem_basics = {"id": problem["problem_id"], "title": problem["title"], "visible": problem["visible"], "exists": True, "assignment": assignment_basics}
                problems.append([problem["problem_id"], problem_basics, course_id, assignment_id])

        return problems

    def get_assignment_statuses(self, course_id, user_id):
        #Gets whether or not a student has passed each assignment in the course.
        assignment_statuses = []
        assignment_dict = {"id": "", "title": "", "passed": 0, "in_progress": 0}

        #FINISH ME - include COUNT for num problems passed and COUNT for total num problems, then calculate "passed" manually
        sql = '''SELECT pass_status.assignment_id,
                        pass_status.title,
                        SUM(pass_status.passed) AS passed,
                        num_status.problem_count
                 FROM
                   (SELECT a.course_id, a.assignment_id, p.problem_id, a.title, IFNULL(MAX(s.passed), 0) AS passed
                    FROM assignments a
                    INNER JOIN problems p
                    ON a.course_id = p.course_id AND a.assignment_id = p.assignment_id
                    LEFT JOIN submissions s
                    ON p.course_id = s.course_id AND p.assignment_id = s.assignment_id AND p.problem_id = s.problem_id
                    WHERE p.course_id = ?
                    AND a.visible = 1
                    AND p.visible = 1
                    AND (s.user_id = ? OR s.user_id IS NULL)
                    GROUP BY a.course_id, a.assignment_id, p.problem_id) pass_status
                 INNER JOIN
                   (SELECT assignment_id, COUNT(problem_id) AS problem_count
                    FROM problems
                    WHERE course_id = ? AND visible = 1
                    GROUP BY course_id, assignment_id) num_status
                 ON pass_status.assignment_id = num_status.assignment_id
                 GROUP BY pass_status.course_id, pass_status.assignment_id
                 ORDER BY pass_status.title'''

        self.c.execute(sql,(str(course_id), str(user_id), str(course_id),))
        for row in self.c.fetchall():
            num_problems = row["problem_count"]
            num_passed = row["passed"]
            if num_problems == num_passed and num_problems > 0:
                passed = 1
                in_progress = 0
            else:
                passed = 0
                if num_passed > 0:
                    in_progress = 1
                else:
                    in_progress = 0
            assignment_dict = {"id": row["assignment_id"], "title": row["title"], "passed": passed, "in_progress": in_progress}
            assignment_statuses.append([row["assignment_id"], assignment_dict])

        return assignment_statuses

    def get_problem_statuses(self, course_id, assignment_id, user_id, show_hidden=True):
        # Gets the number of submissions a student has made for each problem in an assignment and whether or not they've passed the problem.
        problem_statuses = []
        problem_dict = {"id": "", "title": "", "passed": 0, "num_submissions": 0, "in_progress": 0}

        sql = '''SELECT p.problem_id,
                        p.title,
                        IFNULL(MAX(s.passed), 0) AS passed,
                        COUNT(s.submission_id) AS num_submissions
                 FROM problems p
                 LEFT JOIN submissions s
                  ON p.course_id = s.course_id AND p.assignment_id = s.assignment_id AND p.problem_id = s.problem_id
                 WHERE p.course_id = ?
                  AND p.assignment_id = ? 
                  AND (s.user_id = ? OR s.user_id IS NULL)
                  AND p.visible = 1
                 GROUP BY p.assignment_id, p.problem_id
                 ORDER BY p.title'''
        self.c.execute(sql,(course_id, assignment_id, user_id,))

        for row in self.c.fetchall():
            if row["num_submissions"] > 0:
                in_progress = 1
            else:
                in_progress = 0
            problem_dict = {"id": row["problem_id"], "title": row["title"], "passed": row["passed"], "num_submissions": row["num_submissions"], "in_progress": in_progress}
            problem_statuses.append([row["problem_id"], problem_dict])

        return problem_statuses

    def get_assignment_scores(self, course_id, assignment_id):
        #Gets all users who have submitted on a particular assignment and creates a list of their average scores for the assignment.
        scores = []

        sql = '''SELECT a.user_id, SUM(passed) * 100.0 / b.num_problems AS percent_passed
                 FROM
                   (SELECT user_id, IFNULL(MAX(passed), 0) AS passed
                    FROM submissions
                    WHERE course_id = ? AND assignment_id = ?
                    GROUP BY problem_id, user_id) a
                 INNER JOIN
                   (SELECT COUNT(DISTINCT problem_id) AS num_problems
                    FROM problems
                    WHERE course_id = ? AND assignment_id = ? AND visible = 1) b
                    ORDER BY user_id'''

        self.c.execute(sql, (course_id, assignment_id, course_id, assignment_id,))
        for user in self.c.fetchall():
            if user["percent_passed"]:
                user_id = user["user_id"]
                percent_passed = round(user["percent_passed"],2)
                scores_dict = {"user_id": user_id, "percent_passed": percent_passed}
                scores.append([user_id, scores_dict])

        return scores

    def get_submissions_basic(self, course_id, assignment_id, problem_id, user_id):
        submissions = []
        sql = '''SELECT submission_id, date, passed
                 FROM submissions
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND problem_id = ?
                   AND user_id = ?
                  ORDER BY submission_id DESC'''

        self.c.execute(sql, (course_id, assignment_id, problem_id, user_id,))

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

    def specify_problem_details(self, problem_details, instructions, back_end, output_type, answer_code, answer_description, max_submissions, test_code, credit, data_url, data_file_name, data_contents, show_expected, show_test_code, show_answer, expected_output, date_created, date_updated):
        problem_details["instructions"] = instructions
        problem_details["back_end"] = back_end
        problem_details["output_type"] = output_type
        problem_details["answer_code"] = answer_code
        problem_details["answer_description"] = answer_description
        problem_details["max_submissions"] = max_submissions
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
            return {"id": "", "title": "", "visible": True, "exists": False}


        sql = '''SELECT course_id, title, visible
                 FROM courses
                 WHERE course_id = ?'''

        self.c.execute(sql, (course_id,))
        row = self.c.fetchone()

        return {"id": row["course_id"], "title": row["title"], "visible": bool(row["visible"]), "exists": True}

    def get_assignment_basics(self, course_id, assignment_id):
        course_basics = self.get_course_basics(course_id)

        if not assignment_id:
            return {"id": "", "title": "", "visible": True, "exists": False, "course": course_basics}

        sql = '''SELECT assignment_id, title, visible
                 FROM assignments
                 WHERE assignment_id = ?'''

        self.c.execute(sql, (assignment_id,))
        row = self.c.fetchone()

        return {"id": row["assignment_id"], "title": row["title"], "visible": bool(row["visible"]), "exists": True, "course": course_basics}

    def get_problem_basics(self, course_id, assignment_id, problem_id):
        assignment_basics = self.get_assignment_basics(course_id, assignment_id)

        if not problem_id:
            return {"id": "", "title": "", "visible": True, "exists": False, "assignment": assignment_basics}

        sql = '''SELECT problem_id, title, visible
                 FROM problems
                 WHERE problem_id = ?'''

        self.c.execute(sql, (problem_id,))
        row = self.c.fetchone()

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
        if not course:
            return {"introduction": "", "date_created": None, "date_updated": None}

        sql = '''SELECT introduction, date_created, date_updated
                 FROM courses
                 WHERE course_id = ?'''

        self.c.execute(sql, (course,))
        row = self.c.fetchone()

        course_dict = {"introduction": row["introduction"], "date_created": row["date_created"], "date_updated": row["date_updated"]}
        if format_output:
            course_dict["introduction"] = convert_markdown_to_html(course_dict["introduction"])

        return course_dict

    def get_assignment_details(self, course, assignment, format_output=False):
        if not assignment:
            return {"introduction": "", "date_created": None, "date_updated": None}

        sql = '''SELECT introduction, date_created, date_updated
                 FROM assignments
                 WHERE course_id = ? AND assignment_id = ?'''

        self.c.execute(sql, (course, assignment,))
        row = self.c.fetchone()

        assignment_dict = {"introduction": row["introduction"], "date_created": row["date_created"], "date_updated": row["date_updated"]}
        if format_output:
            assignment_dict["introduction"] = convert_markdown_to_html(assignment_dict["introduction"])

        return assignment_dict

    def get_problem_details(self, course, assignment, problem, format_content=False):
        if not problem:
            return {"instructions": "", "back_end": "python",
            "output_type": "txt", "answer_code": "", "answer_description": "", "max_submissions": 0, "test_code": "",
            "credit": "", "show_expected": True, "show_test_code": True, "show_answer": True,
            "expected_output": "", "data_url": "", "data_file_name": "", "data_contents": "",
            "date_created": None, "date_updated": None}

        sql = '''SELECT instructions, back_end, output_type, answer_code, answer_description, max_submissions, test_code, credit, show_expected, show_test_code, show_answer, expected_output, data_url, data_file_name, data_contents, date_created, date_updated
                 FROM problems
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND problem_id = ?'''

        self.c.execute(sql, (course, assignment, problem,))
        row = self.c.fetchone()

        problem_dict = {"instructions": row["instructions"], "back_end": row["back_end"], "output_type": row["output_type"], "answer_code": row["answer_code"], "answer_description": row["answer_description"], "max_submissions": row["max_submissions"], "test_code": row["test_code"], "credit": row["credit"], "show_expected": row["show_expected"], "show_test_code": row["show_test_code"], "show_answer": row["show_answer"], "expected_output": row["expected_output"], "data_url": row["data_url"], "data_file_name": row["data_file_name"], "data_contents": row["data_contents"], "date_created": row["date_created"], "date_updated": row["date_updated"]}

        if format_content:
            problem_dict["instructions"] = convert_markdown_to_html(problem_dict["instructions"])
            problem_dict["credit"] = convert_markdown_to_html(problem_dict["credit"])
            problem_dict["answer_description"] = convert_markdown_to_html(problem_dict["answer_description"])

        return problem_dict

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
            sql = '''INSERT INTO courses (title, visible, introduction, date_created, date_updated)
                     VALUES (?, ?, ?, ?, ?)'''

            self.c.execute(sql, [course_basics["title"], course_basics["visible"], course_details["introduction"], course_details["date_created"], course_details["date_updated"]])
            course_basics["id"] = self.c.lastrowid
            course_basics["exists"] = True

    def save_assignment(self, assignment_basics, assignment_details):
        if assignment_basics["exists"]:
            sql = '''UPDATE assignments
                     SET title = ?, visible = ?, introduction = ?, date_updated = ?
                     WHERE course_id = ? AND assignment_id = ?'''

            self.c.execute(sql, [assignment_basics["title"], assignment_basics["visible"], assignment_details["introduction"], assignment_details["date_updated"], assignment_basics["course"]["id"], assignment_basics["id"]])
        else:
            sql = '''INSERT INTO assignments (course_id, title, visible, introduction, date_created, date_updated)
                     VALUES (?, ?, ?, ?, ?, ?)'''

            self.c.execute(sql, [assignment_basics["course"]["id"], assignment_basics["title"], assignment_basics["visible"], assignment_details["introduction"], assignment_details["date_created"], assignment_details["date_updated"]])
            assignment_basics["id"] = self.c.lastrowid
            assignment_basics["exists"] = True

    def save_problem(self, problem_basics, problem_details):
        if problem_basics["exists"]:
            sql = '''UPDATE problems
                     SET title = ?, visible = ?,
                         answer_code = ?, answer_description = ?, max_submissions = ?, credit = ?, data_url = ?,
                         data_file_name = ?, data_contents = ?, back_end = ?, expected_output = ?,
                         instructions = ?, output_type = ?, show_answer = ?, show_expected = ?,
                         show_test_code = ?, test_code = ?, date_updated = ?
                     WHERE course_id = ? AND assignment_id = ? AND problem_id = ?'''

            self.c.execute(sql, [problem_basics["title"], problem_basics["visible"], str(problem_details["answer_code"]), problem_details["answer_description"], problem_details["max_submissions"], problem_details["credit"], problem_details["data_url"], problem_details["data_file_name"], problem_details["data_contents"], problem_details["back_end"], problem_details["expected_output"], problem_details["instructions"], problem_details["output_type"], problem_details["show_answer"], problem_details["show_expected"], problem_details["show_test_code"], problem_details["test_code"], problem_details["date_updated"], problem_basics["assignment"]["course"]["id"], problem_basics["assignment"]["id"], problem_basics["id"]])
        else:
            sql = '''INSERT INTO problems (course_id, assignment_id, title, visible, answer_code, answer_description, max_submissions, credit, data_url, data_file_name, data_contents, back_end, expected_output, instructions, output_type, show_answer, show_expected, show_test_code, test_code, date_created, date_updated)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

            self.c.execute(sql, [problem_basics["assignment"]["course"]["id"], problem_basics["assignment"]["id"], problem_basics["title"], problem_basics["visible"], str(problem_details["answer_code"]), problem_details["answer_description"], problem_details["max_submissions"], problem_details["credit"], problem_details["data_url"], problem_details["data_file_name"], problem_details["data_contents"], problem_details["back_end"], problem_details["expected_output"], problem_details["instructions"], problem_details["output_type"], problem_details["show_answer"], problem_details["show_expected"], problem_details["show_test_code"], problem_details["test_code"], problem_details["date_created"], problem_details["date_updated"]])
            problem_basics["id"] = self.c.lastrowid
            problem_basics["exists"] = True

    def save_submission(self, course, assignment, problem, user, code, code_output, passed, error_occurred):
        submission_id = self.get_next_submission_id(course, assignment, problem, user)
        sql = '''INSERT INTO submissions (course_id, assignment_id, problem_id, user_id, submission_id, code, code_output, passed, date, error_occurred)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

        self.c.execute(sql, [course, assignment, problem, user, submission_id, code, code_output, passed, datetime.now(), error_occurred])

        return submission_id

    def update_user(self, user_id, user_dict):
        sql = '''UPDATE users
                 SET user_json = ?
                 WHERE user_id = ?'''

        self.c.execute(sql, (json.dumps(user_dict), user_id,))

    def delete_rows_with_value(self, table, col_name, value):
        sql = 'DELETE FROM ' + table + ' WHERE ' + col_name + ' = ?'
        self.c.execute(sql, (value,))

    def delete_all_rows(self, table):
        sql = 'DELETE FROM ' + table
        self.c.execute(sql)

    def delete_problem(self, problem_basics):
        self.delete_problem_submissions(problem_basics)
        self.delete_rows_with_value("problems", "problem_id", problem_basics["id"])

    def delete_assignment(self, assignment_basics):
        self.delete_assignment_submissions(assignment_basics)
        self.delete_rows_with_value("assignments", "assignment_id", assignment_basics["id"])

    def delete_course(self, course_basics):
        self.delete_course_submissions(course_basics)
        self.delete_rows_with_value("courses", "course_id", course_basics["id"])
        self.delete_rows_with_value("permissions", "course_id", course_basics["id"])

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
