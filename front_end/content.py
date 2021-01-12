import atexit
from datetime import datetime, timezone
import glob
import gzip
from helper import *
import html
import io
import json
import math
import os
from queries import *
import re
import sqlite3
import yaml
from yaml import load
from yaml import Loader
import zipfile

class Content:
    def __init__(self, settings_dict):
        self.__settings_dict = settings_dict

        # This enables auto-commit.
        self.conn = sqlite3.connect(f"/database/{settings_dict['db_name']}", isolation_level=None, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys=ON")

        atexit.register(self.close)

    def close(self):
        self.cursor.close()
        self.conn.close()

    def create_sqlite_tables(self):
        create_users_table = '''CREATE TABLE IF NOT EXISTS users (
                                  user_id text PRIMARY KEY,
                                  name text,
                                  given_name text,
                                  family_name text,
                                  picture text,
                                  locale text,
                                  ace_theme text NOT NULL DEFAULT "tomorrow"
                                );'''

        create_permissions_table = '''CREATE TABLE IF NOT EXISTS permissions (
                                        user_id text NOT NULL,
                                        role text NOT NULL,
                                        course_id integer,
                                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE
                                      );'''

        create_course_registration_table = '''CREATE TABLE IF NOT EXISTS course_registration (
                                                 user_id text NOT NULL,
                                                 course_id integer NOT NULL,
                                                 FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                                                 FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE
                                              );'''

        create_courses_table = '''CREATE TABLE IF NOT EXISTS courses (
                                    course_id integer PRIMARY KEY AUTOINCREMENT,
                                    title text NOT NULL UNIQUE,
                                    introduction text,
                                    visible integer NOT NULL,
                                    passcode text,
                                    date_created timestamp NOT NULL,
                                    date_updated timestamp NOT NULL
                                  );'''

        create_assignments_table = '''CREATE TABLE IF NOT EXISTS assignments (
                                        course_id integer NOT NULL,
                                        assignment_id integer PRIMARY KEY AUTOINCREMENT,
                                        title text NOT NULL,
                                        introduction text,
                                        visible integer NOT NULL,
                                        start_date timestamp,
                                        due_date timestamp,
                                        allow_late integer,
                                        late_percent real,
                                        view_answer_late integer,
                                        has_timer int NOT NULL,
                                        hour_timer int,
                                        minute_timer int,
                                        date_created timestamp NOT NULL,
                                        date_updated timestamp NOT NULL,
                                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE
                                      );'''

        create_problems_table = '''CREATE TABLE IF NOT EXISTS problems (
                                     course_id integer NOT NULL,
                                     assignment_id integer NOT NULL,
                                     problem_id integer PRIMARY KEY AUTOINCREMENT,
                                     title text NOT NULL,
                                     visible integer NOT NULL,
                                     answer_code text NOT NULL,
                                     answer_description text,
                                     hint text,
                                     max_submissions integer NOT NULL,
                                     credit text,
                                     data_url text,
                                     data_file_name text,
                                     data_contents text,
                                     back_end text NOT NULL,
                                     expected_text_output text NOT NULL,
                                     expected_image_output text NOT NULL,
                                     instructions text NOT NULL,
                                     output_type text NOT NULL,
                                     show_answer integer NOT NULL,
                                     show_student_submissions integer NOT NULL,
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
                                        text_output text NOT NULL,
                                        image_output text NOT NULL,
                                        passed integer NOT NULL,
                                        date timestamp NOT NULL,
                                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE,
                                        FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE,
                                        FOREIGN KEY (problem_id) REFERENCES problems (problem_id) ON DELETE CASCADE,
                                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                                        PRIMARY KEY (course_id, assignment_id, problem_id, user_id, submission_id)
                                      );'''

        create_scores_table = '''CREATE TABLE IF NOT EXISTS scores (
                                        course_id integer NOT NULL,
                                        assignment_id integer NOT NULL,
                                        problem_id integer NOT NULL,
                                        user_id text NOT NULL,
                                        score real NOT NULL,
                                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE,
                                        FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE,
                                        FOREIGN KEY (problem_id) REFERENCES problems (problem_id) ON DELETE CASCADE,
                                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                                        PRIMARY KEY (course_id, assignment_id, problem_id, user_id)
                                      );'''

        create_user_assignment_start_table = '''CREATE TABLE IF NOT EXISTS user_assignment_start (
                                                  user_id text NOT NULL,
                                                  course_id text NOT NULL,
                                                  assignment_id text NOT NULL,
                                                  start_time timestamp NOT NULL,
                                                  FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE,
                                                  FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE,
                                                  FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
                                                );'''

        if self.conn is not None:
            self.cursor.execute(create_users_table)
            self.cursor.execute(create_permissions_table)
            self.cursor.execute(create_course_registration_table)
            self.cursor.execute(create_courses_table)
            self.cursor.execute(create_assignments_table)
            self.cursor.execute(create_problems_table)
            self.cursor.execute(create_submissions_table)
            self.cursor.execute(create_scores_table)
            self.cursor.execute(create_user_assignment_start_table)
        else:
            print("Error! Cannot create a database connection.")

    def set_start_time(self, course_id, assignment_id, user_id, start_time):
        start_time = datetime.strptime(start_time, "%a, %d %b %Y %H:%M:%S %Z")

        sql = '''INSERT INTO user_assignment_start (course_id, assignment_id, user_id, start_time)
                 VALUES (?, ?, ?, ?)'''

        self.cursor.execute(sql, (course_id, assignment_id, user_id, start_time,))

    def get_start_time(self, course_id, assignment_id, user_id):
        sql = '''SELECT start_time
                 FROM user_assignment_start
                 WHERE course_id = ?
                  AND assignment_id = ?
                  AND user_id = ?'''

        self.cursor.execute(sql, (course_id, assignment_id, user_id,))
        row = self.cursor.fetchone()
        if row:
            return row["start_time"].strftime("%a, %d %b %Y %H:%M:%S %Z")

    def get_all_start_times(self, course_id, assignment_id):
        start_times = {}

        sql = '''SELECT user_id, start_time
                 FROM user_assignment_start
                 WHERE course_id = ?
                  AND assignment_id = ?'''

        self.cursor.execute(sql, (course_id, assignment_id,))
        for row in self.cursor.fetchall():
            start_time = datetime.strftime(row["start_time"], "%a, %d %b %Y %H:%M:%S ")
            timer_ended = self.timer_ended(course_id, assignment_id, start_time)
            time_info = {"start_time": row["start_time"], "timer_ended": timer_ended}
            start_times[row["user_id"]] = time_info

        return start_times

    def timer_ended(self, course_id, assignment_id, start_time):
        if not start_time:
            return False

        curr_time = datetime.now()
        start_time = datetime.strptime(start_time, "%a, %d %b %Y %H:%M:%S ")

        sql = '''SELECT hour_timer, minute_timer
                 FROM assignments
                 WHERE course_id = ?
                 AND assignment_id = ?'''
        self.cursor.execute(sql, (course_id, assignment_id,))
        row = self.cursor.fetchone()

        if row:
            elapsed_time = curr_time - start_time
            seconds = elapsed_time.total_seconds()
            e_hours = math.floor(seconds/3600)
            e_minutes = math.floor((seconds/60) - (e_hours*60))
            e_seconds = (seconds - (e_minutes*60) - (e_hours*3600))

            if e_hours > int(row["hour_timer"]):
                return True
            elif e_hours == int(row["hour_timer"]) and e_minutes > int(row["minute_timer"]):
                return True
            elif e_hours == int(row["hour_timer"]) and e_minutes == int(row["minute_timer"]) and e_seconds > 0:
                return True

        return False

    def reset_timer(self, course_id, assignment_id, user_id):
        sql = '''DELETE FROM user_assignment_start
                 WHERE course_id = ?
                  AND assignment_id = ?
                  AND user_id = ?'''

        self.cursor.execute(sql, (course_id, assignment_id, user_id))

    def user_exists(self, user_id):
        sql = '''SELECT user_id
                 FROM users
                 WHERE user_id = ?'''

        self.cursor.execute(sql, (user_id,))
        return self.cursor.fetchone() != None

    def administrator_exists(self):
        sql = '''SELECT COUNT(*) AS num_administrators
                 FROM permissions
                 WHERE role = "administrator"'''

        self.cursor.execute(sql)
        return self.cursor.fetchone()["num_administrators"]

    def is_administrator(self, user_id):
        return self.user_has_role(user_id, 0, "administrator")

    def is_student(self, user_id):
        sql = '''SELECT role
                 FROM permissions
                 WHERE user_id = ?'''

        self.cursor.execute(sql, (user_id,))
        role = self.cursor.fetchone()
        if role:
            return False
        else:
            return True

    def user_has_role(self, user_id, course_id, role):
        sql = '''SELECT COUNT(*) AS has_role
                 FROM permissions
                 WHERE role = ?
                   AND user_id = ?
                   AND course_id = ?'''

        self.cursor.execute(sql, (role, user_id, course_id, ))
        return self.cursor.fetchone()["has_role"] > 0

    def get_courses_with_role(self, user_id, role):
        sql = '''SELECT course_id
                 FROM permissions
                 WHERE user_id = ?
                   AND role = ?'''

        self.cursor.execute(sql, (user_id, role, ))

        course_ids = set()
        for row in self.cursor.fetchall():
            course_ids.add(row["course_id"])

        return course_ids

    def get_users_from_role(self, course_id, role):
        sql = '''SELECT user_id
                 FROM permissions
                 WHERE role = ?
                   AND (course_id = ? OR course_id IS NULL)'''

        rows = self.cursor.execute(sql, (role, course_id,))
        return [row["user_id"] for row in rows]

    def get_course_id_from_role(self, user_id):
        sql = '''SELECT course_id
                 FROM permissions
                 WHERE user_id = ?'''

        self.cursor.execute(sql, (user_id,))
        row = self.cursor.fetchone()

        if row:
            return row["course_id"]
        else:
            return -1 # The user is a student.

    def add_user(self, user_id, user_dict):
        sql = '''INSERT INTO users (user_id, name, given_name, family_name, picture, locale, ace_theme)
                 VALUES (?, ?, ?, ?, ?, ?, ?)'''

        self.cursor.execute(sql, (user_id, user_dict["name"], user_dict["given_name"], user_dict["family_name"],
        user_dict["picture"], user_dict["locale"], "tomorrow"))

    def register_user_for_course(self, course_id, user_id):
        sql = '''INSERT INTO course_registration (course_id, user_id)
                 VALUES (?, ?)'''

        self.cursor.execute(sql, (course_id, user_id,))
    
    def unregister_user_from_course(self, course_id, user_id):
        sql = '''DELETE FROM course_registration
                 WHERE course_id = ?
                 AND user_id = ?'''
        
        self.cursor.execute(sql, (course_id, user_id,))

    def check_user_registered(self, course_id, user_id):
        sql = '''SELECT *
                 FROM course_registration
                 WHERE course_id = ?
                 AND user_id = ?'''

        self.cursor.execute(sql, (course_id, user_id,))
        if self.cursor.fetchone():
            return True

        return False

    def get_user_info(self, user_id):
        sql = '''SELECT *
                 FROM users
                 WHERE user_id = ?'''

        self.cursor.execute(sql, (user_id,))
        user = self.cursor.fetchone()
        user_info = {"user_id": user_id, "name": user["name"], "given_name": user["given_name"], "family_name": user["family_name"],
                     "picture": user["picture"], "locale": user["locale"], "ace_theme": user["ace_theme"]}

        return user_info

    def add_permissions(self, course_id, user_id, role):
        sql = '''SELECT role
                 FROM permissions
                 WHERE user_id = ?
                   AND (course_id = ? OR course_id IS NULL)'''

        # Admins are not assigned to a particular course.
        if not course_id:
            course_id = 0

        self.cursor.execute(sql, (user_id, int(course_id),))

        role_exists = self.cursor.fetchone() != None

        if role_exists:
            sql = '''UPDATE permissions
                     SET role = ?, course_id = ?
                     WHERE user_id = ?'''

            self.cursor.execute(sql, (role, course_id, user_id,))
        else:
            sql = '''INSERT INTO permissions (user_id, role, course_id)
                     VALUES (?, ?, ?)'''

            self.cursor.execute(sql, (user_id, role, course_id,))

    def remove_permissions(self, course_id, user_id, role):
        sql = '''DELETE FROM permissions
                 WHERE user_id = ?
                   AND role = ?
                   AND (course_id = ? OR course_id IS NULL)'''

        # Admins are not assigned to a particular course.
        if not course_id:
            course_id = "0"

        self.cursor.execute(sql, (user_id, role, int(course_id),))

    def add_admin_permissions(self, user_id):
        self.add_permissions(None, user_id, "administrator")

    def get_user_count(self):
        sql = '''SELECT COUNT(*) AS count
                 FROM users'''

        self.cursor.execute(sql)
        return self.cursor.fetchone()["count"]

    def course_exists(self, course_id):
        sql = '''SELECT COUNT(*) AS count
                 FROM courses
                 WHERE course_id = ?'''
        self.cursor.execute(sql, (course_id,))
        if self.cursor.fetchone():
            return True
        else:
            return False

    def get_courses_connected_to_user(self, user_id):
        courses = []
        sql = '''SELECT p.course_id, c.title
                 FROM permissions p
                 INNER JOIN courses c
                   ON p.course_id = c.course_id
                 WHERE user_id = ?'''

        self.cursor.execute(sql, (user_id,))
        for course in self.cursor.fetchall():
            course_basics = {"id": course["course_id"], "title": course["title"]}
            courses.append([course["course_id"], course_basics])
        return courses

    def get_course_ids(self):
        sql = '''SELECT course_id
                 FROM courses'''

        self.cursor.execute(sql)
        return [course[0] for course in self.cursor.fetchall()]

    def get_assignment_ids(self, course_id):
        if not course_id:
            return []

        sql = '''SELECT assignment_id
                 FROM assignments
                 WHERE course_id = ?'''

        self.cursor.execute(sql, (int(course_id),))
        return [assignment[0] for assignment in self.cursor.fetchall()]

    def get_problem_ids(self, course_id, assignment_id):
        if not assignment_id:
            return []

        sql = '''SELECT problem_id
                 FROM problems
                 WHERE course_id = ?
                   AND assignment_id = ?'''

        self.cursor.execute(sql, (int(course_id), int(assignment_id),))
        return [problem[0] for problem in self.cursor.fetchall()]

    def get_courses(self, show_hidden=True):
        courses = []

        sql = '''SELECT course_id, title, visible, introduction
                 FROM courses
                 ORDER BY title'''
        self.cursor.execute(sql)

        for course in self.cursor.fetchall():
            if course["visible"] or show_hidden:
                course_basics = {"id": course["course_id"], "title": course["title"], "visible": course["visible"], "introduction": course["introduction"], "exists": True}
                courses.append([course["course_id"], course_basics])

        return courses

    def get_assignments(self, course_id, show_hidden=True):
        assignments = []

        sql = '''SELECT c.course_id, c.title as course_title, c.visible as course_visible, a.assignment_id,
                        a.title as assignment_title, a.visible as assignment_visible, a.start_date, a.due_date
                 FROM assignments a
                 INNER JOIN courses c
                  ON c.course_id = a.course_id
                 WHERE c.course_id = ?
                 ORDER BY a.title'''
        self.cursor.execute(sql, (course_id,))

        for row in self.cursor.fetchall():
            if row["assignment_visible"] or show_hidden:
                course_basics = {"id": row["course_id"], "title": row["course_title"], "visible": bool(row["course_visible"]), "exists": True}
                assignment_basics = {"id": row["assignment_id"], "title": row["assignment_title"], "visible": row["assignment_visible"], "start_date": row["start_date"], "due_date": row["due_date"], "exists": False, "course": course_basics}
                assignments.append([row["assignment_id"], assignment_basics])

        return assignments

    def get_problems(self, course_id, assignment_id, show_hidden=True):
        problems = []

        sql = '''SELECT problem_id, title, visible
                 FROM problems
                 WHERE course_id = ?
                   AND assignment_id = ?
                 ORDER BY title'''
        self.cursor.execute(sql, (course_id, assignment_id,))

        for problem in self.cursor.fetchall():
            if problem["visible"] or show_hidden:
                assignment_basics = self.get_assignment_basics(course_id, assignment_id)
                problem_basics = {"id": problem["problem_id"], "title": problem["title"], "visible": problem["visible"], "exists": True, "assignment": assignment_basics}
                problems.append([problem["problem_id"], problem_basics, course_id, assignment_id])

        return problems

    def get_registered_courses(self, user_id):
        registered_courses = []

        sql = '''SELECT r.course_id, c.title
                 FROM course_registration r
                 INNER JOIN courses c
                  ON r.course_id = c.course_id
                 WHERE r.user_id = ?'''

        self.cursor.execute(sql, (user_id,))

        for course in self.cursor.fetchall():
            course_basics = {"id": course["course_id"], "title": course["title"]}
            registered_courses.append([course["course_id"], course_basics])

        return registered_courses

    # Gets whether or not a student has passed each assignment in the course.
    def get_assignment_statuses(self, course_id, user_id):
        sql = '''SELECT assignment_id,
                        title,
                        start_date,
                        due_date,
                        SUM(passed) AS num_passed,
                        COUNT(assignment_id) AS num_problems,
                        SUM(passed) = COUNT(assignment_id) AS passed_all,
                        (SUM(passed) > 0 OR num_submissions > 0) AND SUM(passed) < COUNT(assignment_id) AS in_progress,
                        has_timer,
                        hour_timer,
                        minute_timer
                 FROM (
                   SELECT a.assignment_id,
                          a.title,
                          a.start_date,
                          a.due_date,
                          IFNULL(MAX(s.passed), 0) AS passed,
                          COUNT(s.submission_id) AS num_submissions,
                          a.has_timer,
                          a.hour_timer,
                          a.minute_timer
                   FROM problems p
                   LEFT JOIN submissions s
                     ON p.course_id = s.course_id
                     AND p.assignment_id = s.assignment_id
                     AND p.problem_id = s.problem_id
                     AND (s.user_id = ? OR s.user_id IS NULL)
                   INNER JOIN assignments a
                     ON p.course_id = a.course_id
                     AND p.assignment_id = a.assignment_id
                   WHERE p.course_id = ?
                     AND a.visible = 1
                     AND p.visible = 1
                   GROUP BY p.assignment_id, p.problem_id
                 )
                 GROUP BY assignment_id, title
                 ORDER BY title'''

        self.cursor.execute(sql,(user_id, int(course_id),))

        assignment_statuses = []
        for row in self.cursor.fetchall():
            assignment_dict = {"id": row["assignment_id"], "title": row["title"], "start_date": row["start_date"], "due_date": row["due_date"], "passed": row["passed_all"], "in_progress": row["in_progress"], "num_passed": row["num_passed"], "num_problems": row["num_problems"], "has_timer": row["has_timer"], "hour_timer": row["hour_timer"], "minute_timer": row["minute_timer"]}
            assignment_statuses.append([row["assignment_id"], assignment_dict])

        return assignment_statuses

    # Gets the number of submissions a student has made for each problem
    # in an assignment and whether or not they have passed the problem.
    def get_problem_statuses(self, course_id, assignment_id, user_id, show_hidden=True):
        # This happens when you are creating a new assignment.
        if not assignment_id:
            return []

        sql = '''SELECT p.problem_id,
                        p.title,
                        IFNULL(MAX(s.passed), 0) AS passed,
                        COUNT(s.submission_id) AS num_submissions,
                        COUNT(s.submission_id) > 0 AND IFNULL(MAX(s.passed), 0) = 0 AS in_progress,
                        IFNULL(sc.score, 0) as score
                 FROM problems p
                 LEFT JOIN submissions s
                   ON p.course_id = s.course_id
                   AND p.assignment_id = s.assignment_id
                   AND p.problem_id = s.problem_id
                   AND (s.user_id = ? OR s.user_id IS NULL)
                 LEFT JOIN scores sc
                   ON p.course_id = sc.course_id
                   AND p.assignment_id = sc.assignment_id
                   AND p.problem_id = sc.problem_id
                   AND (s.user_id = sc.user_id OR s.user_id IS NULL)
                 WHERE p.course_id = ?
                   AND p.assignment_id = ?
                   AND p.visible = 1
                 GROUP BY p.assignment_id, p.problem_id
                 ORDER BY p.title'''

        self.cursor.execute(sql,(user_id, int(course_id), int(assignment_id),))

        problem_statuses = []
        for row in self.cursor.fetchall():
            problem_dict = {"id": row["problem_id"], "title": row["title"], "passed": row["passed"], "num_submissions": row["num_submissions"], "in_progress": row["in_progress"], "score": row["score"]}
            problem_statuses.append([row["problem_id"], problem_dict])

        return problem_statuses

    def get_course_scores(self, course_id):
        scores = {}

        sql = assignment_summary_course(course_id)
        self.cursor.execute(sql)

        for row in self.cursor.fetchall():
            scores_dict = {"assignment_id": row["assignment_id"], "title": row["title"], "num_students_completed": row["num_students_completed"], "num_students": row["num_students"], "avg_score": row["avg_score"]}
            scores[row["assignment_id"]] = scores_dict

        return scores

    # Gets all users who have submitted on a particular assignment
    # and creates a list of their average scores for the assignment.
    def get_assignment_scores(self, course_id, assignment_id):
        scores = []

        sql = '''SELECT user_id, (SUM(score) / b.num_problems) AS percent_passed
                 FROM scores
                 INNER JOIN (
                   SELECT COUNT(DISTINCT problem_id) AS num_problems
                   FROM problems
                   WHERE course_id = ?
                     AND assignment_id = ?
                     AND visible = 1
                  ) b
                 WHERE course_id = ?
                  AND assignment_id = ?
                  AND user_id NOT IN
                   (
                    SELECT user_id
                    FROM permissions
                    WHERE course_id = 0 OR course_id IS NULL
                   )
                 GROUP BY course_id, assignment_id, user_id'''

        self.cursor.execute(sql, (int(course_id), int(assignment_id), int(course_id), int(assignment_id),))

        for user in self.cursor.fetchall():
            scores_dict = {"user_id": user["user_id"], "percent_passed": user["percent_passed"]}
            scores.append([user["user_id"], scores_dict])

        return scores

    def get_problem_scores(self, course_id, assignment_id, problem_id):
        scores = []

        sql = '''SELECT s.user_id,
                 sc.score,
                 COUNT(s.submission_id) AS num_submissions
                 FROM submissions s
                 INNER JOIN scores sc
                 ON sc.course_id = s.course_id
                  AND sc.assignment_id = s.assignment_id
                  AND sc.problem_id = s.problem_id
                  AND sc.user_id = s.user_id
                 WHERE s.course_id = ?
                  AND s.assignment_id = ?
                  AND s.problem_id = ?
                 GROUP BY s.user_id
                 ORDER BY s.user_id'''

        self.cursor.execute(sql, (int(course_id), int(assignment_id), int(problem_id),))

        for user in self.cursor.fetchall():
            scores_dict = {"user_id": user["user_id"], "num_submissions": user["num_submissions"], "score": user["score"]}
            scores.append([user["user_id"], scores_dict])

        return scores

    def get_problem_score(self, course_id, assignment_id, problem_id, user_id):
        sql = '''SELECT score
                 FROM scores
                 WHERE course_id = ?
                  AND assignment_id = ?
                  AND problem_id = ?
                  AND user_id = ?'''

        self.cursor.execute(sql, (int(course_id), int(assignment_id), int(problem_id), user_id,))

        row = self.cursor.fetchone()
        if row:
            return row["score"]
        else:
            return None

    def calc_problem_score(self, assignment_details, passed):
        score = 0
        if passed:
            if assignment_details["due_date"] and assignment_details["due_date"] < datetime.now():
                if assignment_details["allow_late"]:
                    score = 100 * assignment_details["late_percent"]
            else:
                score = 100

        return score

    def save_problem_score(self, course_id, assignment_id, problem_id, user_id, new_score):
        score = self.get_problem_score(course_id, assignment_id, problem_id, user_id)

        if score != None:
            sql = '''UPDATE scores
                     SET score = ?
                     WHERE course_id = ?
                      AND assignment_id = ?
                      AND problem_id = ?
                      AND user_id = ?'''

            self.cursor.execute(sql, (new_score, course_id, assignment_id, problem_id, user_id))

        else:
            sql = '''INSERT INTO scores (course_id, assignment_id, problem_id, user_id, score)
                     VALUES (?, ?, ?, ?, ?)'''

            self.cursor.execute(sql, (course_id, assignment_id, problem_id, user_id, new_score))

    def get_submissions_basic(self, course_id, assignment_id, problem_id, user_id):
        submissions = []
        sql = '''SELECT submission_id, date, passed
                 FROM submissions
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND problem_id = ?
                   AND user_id = ?
                 ORDER BY submission_id DESC'''

        self.cursor.execute(sql, (int(course_id), int(assignment_id), int(problem_id), user_id,))

        for submission in self.cursor.fetchall():
            submissions.append([submission["submission_id"], submission["date"].strftime("%a, %d %b %Y %H:%M:%S UTC"), submission["passed"]])
        return submissions

    def get_student_submissions(self, course_id, assignment_id, problem_id, user_id):
        student_submissions = []
        index = 1

        sql = '''SELECT DISTINCT code
                 FROM submissions
                 WHERE course_id = ?
                  AND assignment_id = ?
                  AND problem_id = ?
                  AND passed = 1
                  AND user_id != ?
                 GROUP BY user_id
                 ORDER BY date'''
        
        self.cursor.execute(sql, (course_id, assignment_id, problem_id, user_id,))

        for submission in self.cursor.fetchall():
            student_submissions.append([index, submission["code"]])
            index += 1
        return student_submissions

    def specify_course_basics(self, course_basics, title, visible):
        course_basics["title"] = title
        course_basics["visible"] = visible

    def specify_course_details(self, course_details, introduction, passcode, date_created, date_updated):
        course_details["introduction"] = introduction
        course_details["passcode"] = passcode
        course_details["date_updated"] = date_updated

        if course_details["date_created"]:
            course_details["date_created"] = date_created
        else:
            course_details["date_created"] = date_updated

    def specify_assignment_basics(self, assignment_basics, title, visible):
        assignment_basics["title"] = title
        assignment_basics["visible"] = visible

    def specify_assignment_details(self, assignment_details, introduction, date_created, date_updated, start_date, due_date, allow_late, late_percent, view_answer_late, has_timer, hour_timer, minute_timer):
        assignment_details["introduction"] = introduction
        assignment_details["date_updated"] = date_updated
        assignment_details["start_date"] = start_date
        assignment_details["due_date"] = due_date
        assignment_details["allow_late"] = allow_late
        assignment_details["late_percent"] = late_percent
        assignment_details["view_answer_late"] = view_answer_late
        assignment_details["has_timer"] = has_timer
        assignment_details["hour_timer"] = hour_timer
        assignment_details["minute_timer"] = minute_timer

        if assignment_details["date_created"]:
            assignment_details["date_created"] = date_created
        else:
            assignment_details["date_created"] = date_updated

    def specify_problem_basics(self, problem_basics, title, visible):
        problem_basics["title"] = title
        problem_basics["visible"] = visible

    def specify_problem_details(self, problem_details, instructions, back_end, output_type, answer_code, answer_description, hint, max_submissions, test_code, credit, data_url, data_file_name, data_contents, show_expected, show_test_code, show_answer, show_student_submissions, expected_text_output, expected_image_output, date_created, date_updated):
        problem_details["instructions"] = instructions
        problem_details["back_end"] = back_end
        problem_details["output_type"] = output_type
        problem_details["answer_code"] = answer_code
        problem_details["answer_description"] = answer_description
        problem_details["hint"] = hint
        problem_details["max_submissions"] = max_submissions
        problem_details["test_code"] = test_code
        problem_details["credit"] = credit
        problem_details["data_url"] = data_url
        problem_details["data_file_name"] = data_file_name
        problem_details["data_contents"] = data_contents
        problem_details["show_expected"] = show_expected
        problem_details["show_test_code"] = show_test_code
        problem_details["show_answer"] = show_answer
        problem_details["show_student_submissions"] = show_student_submissions
        problem_details["expected_text_output"] = expected_text_output
        problem_details["expected_image_output"] = expected_image_output
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

        self.cursor.execute(sql, (int(course_id),))
        row = self.cursor.fetchone()

        return {"id": row["course_id"], "title": row["title"], "visible": bool(row["visible"]), "exists": True}

    def get_assignment_basics(self, course_id, assignment_id):
        course_basics = self.get_course_basics(course_id)

        if not assignment_id:
            return {"id": "", "title": "", "visible": True, "exists": False, "course": course_basics}

        sql = '''SELECT assignment_id, title, visible
                 FROM assignments
                 WHERE course_id = ?
                   AND assignment_id = ?'''

        self.cursor.execute(sql, (int(course_id), int(assignment_id),))
        row = self.cursor.fetchone()
        if row is None:
            return {"id": "", "title": "", "visible": True, "exists": False, "course": course_basics}
        else:
            return {"id": row["assignment_id"], "title": row["title"], "visible": bool(row["visible"]), "exists": True, "course": course_basics}

    def get_problem_basics(self, course_id, assignment_id, problem_id):
        assignment_basics = self.get_assignment_basics(course_id, assignment_id)

        if not problem_id:
            return {"id": "", "title": "", "visible": True, "exists": False, "assignment": assignment_basics}

        sql = '''SELECT problem_id, title, visible
                 FROM problems
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND problem_id = ?'''

        self.cursor.execute(sql, (int(course_id), int(assignment_id), int(problem_id),))
        row = self.cursor.fetchone()
        if row is None:
            return {"id": "", "title": "", "visible": True, "exists": False, "assignment": assignment_basics}
        else:
            return {"id": row["problem_id"], "title": row["title"], "visible": bool(row["visible"]), "exists": True, "assignment": assignment_basics}

    def get_next_prev_problems(self, course, assignment, problem, problems):
        prev_problem = None
        next_problem = None

        if len(problems) > 0 and problem:
            this_problem = [i for i in range(len(problems)) if problems[i][0] == int(problem)]
            if len(this_problem) > 0:
                this_problem_index = [i for i in range(len(problems)) if problems[i][0] == int(problem)][0]

                if len(problems) >= 2 and this_problem_index != 0:
                    prev_problem = problems[this_problem_index - 1][1]

                if len(problems) >= 2 and this_problem_index != (len(problems) - 1):
                    next_problem = problems[this_problem_index + 1][1]

        return {"previous": prev_problem, "next": next_problem}

    def get_num_submissions(self, course, assignment, problem, user):
        sql = '''SELECT COUNT(*)
                 FROM submissions
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND problem_id = ?
                   AND user_id = ?'''

        return self.cursor.execute(sql, (int(course), int(assignment), int(problem), user,)).fetchone()[0]

    def get_next_submission_id(self, course, assignment, problem, user):
        return self.get_num_submissions(course, assignment, problem, user) + 1

    def get_last_submission(self, course, assignment, problem, user):
        last_submission_id = self.get_num_submissions(course, assignment, problem, user)

        if last_submission_id > 0:
            return self.get_submission_info(course, assignment, problem, user, last_submission_id)
        else:
            return None

    def get_submission_info(self, course, assignment, problem, user, submission):
        sql = '''SELECT code, text_output, image_output, passed, date
                 FROM submissions
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND problem_id = ?
                   AND user_id = ?
                   AND submission_id = ?'''

        self.cursor.execute(sql, (int(course), int(assignment), int(problem), user, int(submission),))
        row = self.cursor.fetchone()

        return {"id": submission, "code": row["code"], "text_output": row["text_output"], "image_output": row["image_output"], "passed": row["passed"], "date": row["date"].strftime("%m/%d/%Y, %I:%M:%S %p"), "exists": True}

    def get_course_details(self, course, format_output=False):
        if not course:
            return {"introduction": "", "passcode": None, "date_created": None, "date_updated": None}

        sql = '''SELECT introduction, passcode, date_created, date_updated
                 FROM courses
                 WHERE course_id = ?'''

        self.cursor.execute(sql, (int(course),))
        row = self.cursor.fetchone()

        course_dict = {"introduction": row["introduction"], "passcode": row["passcode"], "date_created": row["date_created"], "date_updated": row["date_updated"]}
        if format_output:
            course_dict["introduction"] = convert_markdown_to_html(course_dict["introduction"])

        return course_dict

    def get_assignment_details(self, course, assignment, format_output=False):
        if not assignment:
            return {"introduction": "", "date_created": None, "date_updated": None, "start_date": None, "due_date": None, "allow_late": False, "late_percent": None, "view_answer_late": False, "has_timer": 0, "hour_timer": None, "minute_timer": None}

        sql = '''SELECT introduction, date_created, date_updated, start_date, due_date, allow_late, late_percent, view_answer_late, has_timer, hour_timer, minute_timer
                 FROM assignments
                 WHERE course_id = ?
                   AND assignment_id = ?'''

        self.cursor.execute(sql, (int(course), int(assignment),))
        row = self.cursor.fetchone()

        assignment_dict = {"introduction": row["introduction"], "date_created": row["date_created"], "date_updated": row["date_updated"], "start_date": row["start_date"], "due_date": row["due_date"], "allow_late": row["allow_late"], "late_percent": row["late_percent"], "view_answer_late": row["view_answer_late"], "has_timer": row["has_timer"], "hour_timer": row["hour_timer"], "minute_timer": row["minute_timer"]}
        if format_output:
            assignment_dict["introduction"] = convert_markdown_to_html(assignment_dict["introduction"])

        return assignment_dict

    def get_problem_details(self, course, assignment, problem, format_content=False):
        if not problem:
            return {"instructions": "", "back_end": "python",
            "output_type": "txt", "answer_code": "", "answer_description": "", "hint": "", "max_submissions": 0, "test_code": "",
            "credit": "", "show_expected": True, "show_test_code": True, "show_answer": True, "show_student_submissions": False,
            "expected_text_output": "", "expected_image_output": "", "data_url": "", "data_file_name": "", "data_contents": "",
            "date_created": None, "date_updated": None}

        sql = '''SELECT instructions, back_end, output_type, answer_code, answer_description, hint, max_submissions, test_code, credit, show_expected, show_test_code, show_answer, show_student_submissions, expected_text_output, expected_image_output, data_url, data_file_name, data_contents, date_created, date_updated
                 FROM problems
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND problem_id = ?'''

        self.cursor.execute(sql, (int(course), int(assignment), int(problem),))
        row = self.cursor.fetchone()

        problem_dict = {"instructions": row["instructions"], "back_end": row["back_end"], "output_type": row["output_type"], "answer_code": row["answer_code"], "answer_description": row["answer_description"], "hint": row["hint"], "max_submissions": row["max_submissions"], "test_code": row["test_code"], "credit": row["credit"], "show_expected": row["show_expected"], "show_test_code": row["show_test_code"], "show_answer": row["show_answer"], "show_student_submissions": row["show_student_submissions"], "expected_text_output": row["expected_text_output"], "expected_image_output": row["expected_image_output"], "data_url": row["data_url"], "data_file_name": row["data_file_name"], "data_contents": row["data_contents"], "date_created": row["date_created"], "date_updated": row["date_updated"]}

        if format_content:
            problem_dict["expected_text_output"] = format_output_as_html(problem_dict["expected_text_output"])
            problem_dict["instructions"] = convert_markdown_to_html(problem_dict["instructions"])
            problem_dict["credit"] = convert_markdown_to_html(problem_dict["credit"])
            problem_dict["answer_description"] = convert_markdown_to_html(problem_dict["answer_description"])
            problem_dict["hint"] =  convert_markdown_to_html(problem_dict["hint"])

        return problem_dict

    def get_log_table_contents(self, file_path, year="No filter", month="No filter", day="No filter"):
        new_dict = {}
        line_num = 1
        with gzip.open(file_path) as read_file:
            header = read_file.readline()
            for line in read_file:
                line_items = line.decode().rstrip("\n").split("\t")

                #Get ids to create links to each course, assignment, and problem in the table
                course_id = line_items[1]
                assignment_id = line_items[2]
                problem_id = line_items[3]

                line_items[6] = f"<a href='/course/{course_id}'>{line_items[6]}</a>"
                line_items[7] = f"<a href='/assignment/{course_id}/{assignment_id}'>{line_items[7]}</a>"
                line_items[8] = f"<a href='/problem/{course_id}/{assignment_id}/{problem_id}'>{line_items[8]}</a>"

                line_items = [line_items[0][:2], line_items[0][2:4], line_items[0][4:6], line_items[0][6:]] + line_items[4:]

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
                     SET title = ?, visible = ?, introduction = ?, passcode = ?, date_updated = ?
                     WHERE course_id = ?'''

            self.cursor.execute(sql, [course_basics["title"], course_basics["visible"], course_details["introduction"], course_details["passcode"], course_details["date_updated"], course_basics["id"]])
        else:
            sql = '''INSERT INTO courses (title, visible, introduction, passcode, date_created, date_updated)
                     VALUES (?, ?, ?, ?, ?, ?)'''

            self.cursor.execute(sql, [course_basics["title"], course_basics["visible"], course_details["introduction"], course_details["passcode"], course_details["date_created"], course_details["date_updated"]])
            course_basics["id"] = self.cursor.lastrowid
            course_basics["exists"] = True

        return course_basics["id"]

    def save_assignment(self, assignment_basics, assignment_details):
        if assignment_basics["exists"]:
            sql = '''UPDATE assignments
                     SET title = ?, visible = ?, introduction = ?, date_updated = ?, start_date = ?, due_date = ?, allow_late = ?, late_percent = ?, view_answer_late = ?, has_timer = ?, hour_timer = ?, minute_timer = ?
                     WHERE course_id = ?
                       AND assignment_id = ?'''

            self.cursor.execute(sql, [assignment_basics["title"], assignment_basics["visible"], assignment_details["introduction"], assignment_details["date_updated"], assignment_details["start_date"], assignment_details["due_date"], assignment_details["allow_late"], assignment_details["late_percent"], assignment_details["view_answer_late"], assignment_details["has_timer"], assignment_details["hour_timer"], assignment_details["minute_timer"], assignment_basics["course"]["id"], assignment_basics["id"]])
        else:
            sql = '''INSERT INTO assignments (course_id, title, visible, introduction, date_created, date_updated, start_date, due_date, allow_late, late_percent, view_answer_late, has_timer, hour_timer, minute_timer)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

            self.cursor.execute(sql, [assignment_basics["course"]["id"], assignment_basics["title"], assignment_basics["visible"], assignment_details["introduction"], assignment_details["date_created"], assignment_details["date_updated"], assignment_details["start_date"], assignment_details["due_date"], assignment_details["allow_late"], assignment_details["late_percent"], assignment_details["view_answer_late"], assignment_details["has_timer"], assignment_details["hour_timer"], assignment_details["minute_timer"]])

            assignment_basics["id"] = self.cursor.lastrowid
            assignment_basics["exists"] = True

        return assignment_basics["id"]

    def save_problem(self, problem_basics, problem_details):
        if problem_basics["exists"]:
            sql = '''UPDATE problems
                     SET title = ?, visible = ?,
                         answer_code = ?, answer_description = ?, hint = ?, max_submissions = ?, credit = ?, data_url = ?,
                         data_file_name = ?, data_contents = ?, back_end = ?, expected_text_output = ?, expected_image_output = ?,
                         instructions = ?, output_type = ?, show_answer = ?, show_student_submissions = ?, show_expected = ?,
                         show_test_code = ?, test_code = ?, date_updated = ?
                     WHERE course_id = ?
                       AND assignment_id = ?
                       AND problem_id = ?'''

            self.cursor.execute(sql, [problem_basics["title"], problem_basics["visible"], str(problem_details["answer_code"]), problem_details["answer_description"], problem_details["hint"], problem_details["max_submissions"], problem_details["credit"], problem_details["data_url"], problem_details["data_file_name"], problem_details["data_contents"], problem_details["back_end"], problem_details["expected_text_output"], problem_details["expected_image_output"], problem_details["instructions"], problem_details["output_type"], problem_details["show_answer"], problem_details["show_student_submissions"], problem_details["show_expected"], problem_details["show_test_code"], problem_details["test_code"], problem_details["date_updated"], problem_basics["assignment"]["course"]["id"], problem_basics["assignment"]["id"], problem_basics["id"]])
        else:
            sql = '''INSERT INTO problems (course_id, assignment_id, title, visible, answer_code, answer_description, hint, max_submissions, credit, data_url, data_file_name, data_contents, back_end, expected_text_output, expected_image_output, instructions, output_type, show_answer, show_student_submissions, show_expected, show_test_code, test_code, date_created, date_updated)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

            self.cursor.execute(sql, [problem_basics["assignment"]["course"]["id"], problem_basics["assignment"]["id"], problem_basics["title"], problem_basics["visible"], str(problem_details["answer_code"]), problem_details["answer_description"], problem_details["hint"], problem_details["max_submissions"], problem_details["credit"], problem_details["data_url"], problem_details["data_file_name"], problem_details["data_contents"], problem_details["back_end"], problem_details["expected_text_output"], problem_details["expected_image_output"], problem_details["instructions"], problem_details["output_type"], problem_details["show_answer"], problem_details["show_student_submissions"], problem_details["show_expected"], problem_details["show_test_code"], problem_details["test_code"], problem_details["date_created"], problem_details["date_updated"]])
            problem_basics["id"] = self.cursor.lastrowid
            problem_basics["exists"] = True

        return problem_basics["id"]

    def save_submission(self, course, assignment, problem, user, code, text_output, image_output, passed):
        submission_id = self.get_next_submission_id(course, assignment, problem, user)
        sql = '''INSERT INTO submissions (course_id, assignment_id, problem_id, user_id, submission_id, code, text_output, image_output, passed, date)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

        self.cursor.execute(sql, [int(course), int(assignment), int(problem), user, int(submission_id), code, text_output, image_output, passed, datetime.now()])

        return submission_id

    def copy_assignment(self, course_id, assignment_id, new_course_id):
        sql = '''INSERT INTO assignments (course_id, title, visible, introduction, date_created, date_updated, start_date, due_date, allow_late, late_percent, view_answer_late, has_timer, hour_timer, minute_timer)
                 SELECT ?, title, visible, introduction, date_created, date_updated, start_date, due_date, allow_late, late_percent, view_answer_late, has_timer, hour_timer, minute_timer
                 FROM assignments
                 WHERE course_id = ?
                   AND assignment_id = ?'''

        self.cursor.execute(sql, (new_course_id, course_id, assignment_id,))
        new_assignment_id = self.cursor.lastrowid

        sql = '''INSERT INTO problems (course_id, assignment_id, title, visible, answer_code, answer_description, max_submissions, credit, data_url, data_file_name, data_contents, back_end, expected_text_output, expected_image_output, instructions, output_type, show_answer, show_expected, show_test_code, test_code, date_created, date_updated)
                 SELECT ?, ?, title, visible, answer_code, answer_description, max_submissions, credit, data_url, data_file_name, data_contents, back_end, expected_text_output, expected_image_output, instructions, output_type, show_answer, show_expected, show_test_code, test_code, date_created, date_updated
                 FROM problems
                 WHERE course_id = ?
                   AND assignment_id = ?'''

        self.cursor.execute(sql, (new_course_id, new_assignment_id, course_id, assignment_id,))

    def update_user(self, user_id, user_dict):
        sql = '''UPDATE users
                 SET name = ?, given_name = ?, family_name = ?, picture = ?, locale = ?
                 WHERE user_id = ?'''

        name = "[Unknown name]"
        given_name = "[Unknown given name]"
        family_name = "[Unknown family name]"
        picture = ""
        locale = ""

        if "name" in user_dict:
            name = user_dict["name"]
        if "given_name" in user_dict:
            given_name = user_dict["given_name"]
        if "family_name" in user_dict:
            family_name = user_dict["family_name"]
        if "picture" in user_dict:
            picture = user_dict["picture"]
        if "locale" in user_dict:
            locale = user_dict["locale"]

        self.cursor.execute(sql, (name, given_name, family_name, picture, locale, user_id,))

    def update_user_settings(self, user_id, theme):
        sql = '''UPDATE users
                 SET ace_theme = ?
                 WHERE user_id = ?'''
        self.cursor.execute(sql, (theme, user_id,))

    def remove_user_submissions(self, user_id):
        sql = '''SELECT submission_id
                 FROM submissions
                 WHERE user_id = ?'''

        self.cursor.execute(sql, (user_id,))
        submissions = self.cursor.fetchall()
        if submissions:

            sql = '''DELETE FROM scores
                     WHERE user_id = ?'''
            self.cursor.execute(sql, (user_id,))

            sql = '''DELETE FROM submissions
                     WHERE user_id = ?'''
            self.cursor.execute(sql, (user_id,))

            return True
        else:
            return False

    def delete_user(self, user_id):
        sql = f'''DELETE FROM users
                  WHERE user_id = ?'''

        self.cursor.execute(sql, (user_id,))

    def move_problem(self, course_id, assignment_id, problem_id, new_assignment_id):
        sql = '''UPDATE problems
                 SET assignment_id = ?
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND problem_id = ?'''

        self.cursor.execute(sql, (new_assignment_id, course_id, assignment_id, problem_id))

    def delete_problem(self, problem_basics):
        c_id = problem_basics["assignment"]["course"]["id"]
        a_id = problem_basics["assignment"]["id"]
        p_id = problem_basics["id"]

        sql = f'''BEGIN TRANSACTION;

                 DELETE FROM submissions
                 WHERE course_id = {c_id}
                   AND assignment_id = {a_id}
                   AND problem_id = {p_id};

                 DELETE FROM problems
                 WHERE course_id = {c_id}
                   AND assignment_id = {a_id}
                   AND problem_id = {p_id};

                 COMMIT;
              '''

        self.cursor.executescript(sql)

    def delete_assignment(self, assignment_basics):
        c_id = assignment_basics["course"]["id"]
        a_id = assignment_basics["id"]

        sql = f'''BEGIN TRANSACTION;

                 DELETE FROM submissions
                 WHERE course_id = {c_id}
                   AND assignment_id = {a_id};

                 DELETE FROM problems
                 WHERE course_id = {c_id}
                   AND assignment_id = {a_id};

                 DELETE FROM assignments
                 WHERE course_id = {c_id}
                   AND assignment_id = {a_id};

                 COMMIT;
              '''

        self.cursor.executescript(sql)

    def delete_course(self, course_basics):
        c_id = course_basics["id"]

        sql = f'''BEGIN TRANSACTION;

                 DELETE FROM submissions
                 WHERE course_id = {c_id};

                 DELETE FROM problems
                 WHERE course_id = {c_id};

                 DELETE FROM assignments
                 WHERE course_id = {c_id};

                 DELETE FROM courses
                 WHERE course_id = {c_id};

                 DELETE FROM permissions
                 WHERE course_id = {c_id};

                 COMMIT;
              '''

        self.cursor.executescript(sql)

    def delete_course_submissions(self, course_basics):
        sql = '''DELETE FROM submissions
                 WHERE course_id = ?'''

        self.cursor.execute(sql, (course_basics["id"],))

    def delete_assignment_submissions(self, assignment_basics):
        sql = '''DELETE FROM submissions
                 WHERE course_id = ?
                   AND assignment_id = ?'''

        self.cursor.execute(sql, (assignment_basics["course"]["id"], assignment_basics["id"],))

    def delete_problem_submissions(self, problem_basics):
        sql = '''DELETE FROM submissions
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND problem_id = ?'''

        self.cursor.execute(sql, (problem_basics["assignment"]["course"]["id"], problem_basics["assignment"]["id"], problem_basics["id"],))

    #TODO: Modify the logic so that we use the SQLite dump functionality rather than custom logic.
    #TODO: Make sure we include Emme's new table(s) in this?
    def create_scores_text(self, course_id, assignment_id):
        out_file_text = "Course_ID,Assignment_ID,Student_ID,Score\n"
        scores = self.get_assignment_scores(course_id, assignment_id)

        for student in scores:
            out_file_text += f"{course_id},{assignment_id},{student[0]},{student[1]['percent_passed']}\n"

        return out_file_text

    def export_data(self, course_basics, table_name, output_tsv_file_path):
        if table_name == "submissions":
            sql = '''SELECT c.title, a.title, p.title, s.user_id, s.submission_id, s.code, s.text_output, s.image_output, s.passed, s.date
                    FROM submissions s
                    INNER JOIN courses c
                      ON c.course_id = s.course_id
                    INNER JOIN assignments a
                      ON a.assignment_id = s.assignment_id
                    INNER JOIN problems p
                      ON p.problem_id = s.problem_id
                    WHERE s.course_id = ?'''

        else:
            sql = f"SELECT * FROM {table_name} WHERE course_id = ?"

        self.cursor.execute(sql, (course_basics["id"],))

        rows = []
        for row in self.cursor.fetchall():
            row_values = []
            for x in row:
                if type(x) is datetime:
                    x = str(x)
                row_values.append(x)

            rows.append(row_values)

        with open(output_tsv_file_path, "w") as out_file:
            out_file.write(json.dumps(rows))

    def create_zip_file_path(self, descriptor):
        temp_dir_path = "/database/tmp/{}".format(create_id())
        zip_file_name = f"{descriptor}.zip"
        zip_file_path = f"{temp_dir_path}/{zip_file_name}"
        return temp_dir_path, zip_file_name, zip_file_path

    def zip_export_files(self, temp_dir_path, zip_file_name, zip_file_path, descriptor):
        os.system(f"cp VERSION {temp_dir_path}/{descriptor}/")
        os.system(f"cd {temp_dir_path}; zip -r -qq {zip_file_path} .")

    def create_export_paths(self, temp_dir_path, descriptor):
        os.makedirs(temp_dir_path)
        os.makedirs(f"{temp_dir_path}/{descriptor}")

    def remove_export_paths(self, zip_file_path, tmp_dir_path):
        if os.path.exists(zip_file_path):
            os.remove(zip_file_path)

        if os.path.exists(tmp_dir_path):
            shutil.rmtree(tmp_dir_path, ignore_errors=True)

    def rebuild_problems(self, assignment_title):
        sql = '''SELECT p.*
                 FROM problems p
                 INNER JOIN assignments a
                   ON p.course_id = a.course_id AND p.assignment_id = a.assignment_id
                 WHERE a.title = ?'''
        self.cursor.execute(sql, (assignment_title, ))

        for row in self.cursor.fetchall():
            course = row["course_id"]
            assignment = row["assignment_id"]
            problem = row["problem_id"]
            print(f"Rebuilding course {course}, assignment {assignment}, exercise {problem}")

            problem_basics = self.get_problem_basics(course, assignment, problem)
            problem_details = self.get_problem_details(course, assignment, problem)

            text_output, image_output = exec_code(self.__settings_dict, problem_details["answer_code"], problem_basics, problem_details)

            problem_details["expected_text_output"] = text_output
            problem_details["expected_image_output"] = image_output
            self.save_problem(problem_basics, problem_details)

    def rerun_submissions(self, assignment_title):
        sql = '''SELECT course_id, assignment_id
                 FROM assignments
                 WHERE title = ?'''
        self.cursor.execute(sql, (assignment_title, ))
        row = self.cursor.fetchone()
        course = int(row["course_id"])
        assignment = int(row["assignment_id"])

        sql = '''SELECT *
                 FROM submissions
                 WHERE course_id = ? AND assignment_id = ? AND passed = 0
                 ORDER BY problem_id, user_id, submission_id'''
        self.cursor.execute(sql, (course, assignment, ))

        for row in self.cursor.fetchall():
            problem = row["problem_id"]
            user = row["user_id"]
            submission = row["submission_id"]
            code = row["code"].replace("\r", "")
            print(f"Rerunning submission {submission} for course {course}, assignment {assignment}, exercise {problem}, user {user}.")

            problem_basics = self.get_problem_basics(course, assignment, problem)
            problem_details = self.get_problem_details(course, assignment, problem)

            text_output, image_output = exec_code(self.__settings_dict, code, problem_basics, problem_details, None)
            diff, passed = check_problem_output(problem_details["expected_text_output"], text_output, problem_details["expected_image_output"], image_output, problem_details["output_type"])

            sql = '''UPDATE submissions
                     SET text_output = ?,
                         image_output = ?,
                         passed = ?
                     WHERE course_id = ?
                       AND assignment_id = ?
                       AND problem_id = ?
                       AND user_id = ?
                       AND submission_id = ?'''

            self.cursor.execute(sql, [text_output, image_output, passed, int(course), int(assignment), int(problem), user, int(submission)])
