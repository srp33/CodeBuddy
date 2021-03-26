import atexit
from datetime import datetime, timezone
import glob
import gzip
from helper import *
import html
from imgcompare import *
import io
import json
import math
import os
from queries import *
import re
import spacy
import sqlite3
import yaml
from yaml import load
from yaml import Loader
import zipfile

class Content:
    def __init__(self, settings_dict):
        self.__settings_dict = settings_dict

        # This enables auto-commit.
        self.conn = sqlite3.connect(f"/database/{settings_dict['db_name']}",
                isolation_level = None,
                detect_types = sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES,
                timeout = 10)
        self.conn.row_factory = sqlite3.Row
        #self.execute("PRAGMA foreign_keys=ON")
        self.execute("PRAGMA foreign_keys=OFF")

        atexit.register(self.close)

    def close(self):
        self.conn.close()

    def execute(self, sql, params=()):
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        lastrowid = cursor.lastrowid
        cursor.close()

        return lastrowid

    def fetchone(self, sql, params=()):
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        result = cursor.fetchone()
        cursor.close()

        return result

    def fetchall(self, sql, params=()):
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        result = cursor.fetchall()
        cursor.close()

        return result

    # This function creates tables as they were in version 5. Subsequent changes
    #   to the database are implemented as migration scripts.
    def create_database_tables(self):
        for sql in database_tables():
            self.execute(sql)

    def get_database_version(self):
        sql = '''SELECT MAX(version) AS version
                 FROM metadata'''

        return self.fetchone(sql)["version"]

    def update_database_version(self, version):
        sql = '''DELETE FROM metadata'''
        self.execute(sql)

        sql = '''INSERT INTO metadata (version)
                 VALUES (?)'''
        self.execute(sql, (version,))

    def set_user_assignment_start_time(self, course_id, assignment_id, user_id, start_time):
        start_time = datetime.strptime(start_time, "%a, %d %b %Y %H:%M:%S %Z")

        sql = '''INSERT INTO user_assignment_starts (course_id, assignment_id, user_id, start_time)
                 VALUES (?, ?, ?, ?)'''

        self.execute(sql, (course_id, assignment_id, user_id, start_time,))

    def get_user_assignment_start_time(self, course_id, assignment_id, user_id):
        sql = '''SELECT start_time
                 FROM user_assignment_starts
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND user_id = ?'''

        row = self.fetchone(sql, (course_id, assignment_id, user_id,))
        if row:
            return row["start_time"].strftime("%a, %d %b %Y %H:%M:%S %Z")

    def get_all_user_assignment_start_times(self, course_id, assignment_id):
        start_times = {}

        sql = '''SELECT user_id, start_time
                 FROM user_assignment_starts
                 WHERE course_id = ?
                   AND assignment_id = ?'''

        for row in self.fetchall(sql, (course_id, assignment_id,)):
            start_time = datetime.strftime(row["start_time"], "%a, %d %b %Y %H:%M:%S ")
            timer_ended = self.has_user_assignment_start_timer_ended(course_id, assignment_id, start_time)
            time_info = {"start_time": row["start_time"], "timer_ended": timer_ended}
            start_times[row["user_id"]] = time_info

        return start_times

    def has_user_assignment_start_timer_ended(self, course_id, assignment_id, start_time):
        if not start_time:
            return False

        curr_time = datetime.now()
        start_time = datetime.strptime(start_time, "%a, %d %b %Y %H:%M:%S ")

        sql = '''SELECT hour_timer, minute_timer
                 FROM assignments
                 WHERE course_id = ?
                   AND assignment_id = ?'''
        row = self.fetchone(sql, (course_id, assignment_id,))

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

    def reset_user_assignment_start_timer(self, course_id, assignment_id, user_id):
        sql = '''DELETE FROM user_assignment_starts
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND user_id = ?'''

        self.execute(sql, (course_id, assignment_id, user_id))

    def user_exists(self, user_id):
        sql = '''SELECT user_id
                 FROM users
                 WHERE user_id = ?'''

        return self.fetchone(sql, (user_id,)) != None

    def administrator_exists(self):
        sql = '''SELECT COUNT(*) AS num_administrators
                 FROM permissions
                 WHERE role = "administrator"'''

        return self.fetchone(sql)["num_administrators"]

    def is_administrator(self, user_id):
        return self.user_has_role(user_id, 0, "administrator")

    def user_has_role(self, user_id, course_id, role):
        sql = '''SELECT COUNT(*) AS has_role
                 FROM permissions
                 WHERE role = ?
                   AND user_id = ?
                   AND course_id = ?'''

        return self.fetchone(sql, (role, user_id, course_id, ))["has_role"] > 0

    def get_courses_with_role(self, user_id, role):
        sql = '''SELECT course_id
                 FROM permissions
                 WHERE user_id = ?
                   AND role = ?'''

        course_ids = set()
        for row in self.fetchall(sql, (user_id, role, )):
            course_ids.add(row["course_id"])

        return course_ids

    def get_users_from_role(self, course_id, role):
        sql = '''SELECT user_id
                 FROM permissions
                 WHERE role = ?
                   AND (course_id = ? OR course_id IS NULL)'''

        rows = self.fetchall(sql, (role, course_id,))
        return [row["user_id"] for row in rows]

    def get_course_id_from_role(self, user_id):
        sql = '''SELECT course_id
                 FROM permissions
                 WHERE user_id = ?'''

        row = self.fetchone(sql, (user_id,))

        if row:
            return row["course_id"]
        else:
            return -1 # The user is a student.

    def set_user_dict_defaults(self, user_dict):
        if "name" not in user_dict:
            user_dict["name"] = "[Unknown name]"
        if "given_name" not in user_dict:
            user_dict["given_name"] = "[Unknown given name]"
        if "family_name" not in user_dict:
            user_dict["family_name"] = "[Unknown family name]"
        if "picture" not in user_dict:
            user_dict["picture"] = ""
        if "locale" not in user_dict:
            user_dict["locale"] = ""

    def add_user(self, user_id, user_dict):
        self.set_user_dict_defaults(user_dict)

        sql = '''INSERT INTO users (user_id, name, given_name, family_name, picture, locale, ace_theme)
                 VALUES (?, ?, ?, ?, ?, ?, ?)'''

        self.execute(sql, (user_id, user_dict["name"], user_dict["given_name"], user_dict["family_name"],
        user_dict["picture"], user_dict["locale"], "tomorrow"))

    def register_user_for_course(self, course_id, user_id):
        sql = '''INSERT INTO course_registrations (course_id, user_id)
                 VALUES (?, ?)'''

        self.execute(sql, (course_id, user_id,))

    def unregister_user_from_course(self, course_id, user_id):
        self.execute(f'''DELETE FROM course_registrations
                                WHERE course_id = {course_id}
                                  AND user_id = '{user_id}' ''')

        self.execute(f'''DELETE FROM scores
                                WHERE course_id = {course_id}
                                  AND user_id = '{user_id}' ''')

        self.execute(f'''DELETE FROM submissions
                                WHERE course_id = {course_id}
                                  AND user_id = '{user_id}' ''')

        self.execute(f'''DELETE FROM user_assignment_starts
                                WHERE course_id = {course_id}
                                  AND user_id = '{user_id}' ''')

    def check_user_registered(self, course_id, user_id):
        sql = '''SELECT 1
                 FROM course_registrations
                 WHERE course_id = ?
                   AND user_id = ?'''

        if self.fetchone(sql, (course_id, user_id,)):
            return True

        return False

    def get_user_info(self, user_id):
        sql = '''SELECT *
                 FROM users
                 WHERE user_id = ?'''

        user = self.fetchone(sql, (user_id,))
        user_info = {"user_id": user_id, "name": user["name"], "given_name": user["given_name"], "family_name": user["family_name"],
                     "picture": user["picture"], "locale": user["locale"], "ace_theme": user["ace_theme"], "use_auto_complete": user["use_auto_complete"]}

        return user_info

    def add_permissions(self, course_id, user_id, role):
        sql = '''SELECT role
                 FROM permissions
                 WHERE user_id = ?
                   AND (course_id = ? OR course_id IS NULL)'''

        # Admins are not assigned to a particular course.
        if not course_id:
            course_id = 0

        role_exists = self.fetchone(sql, (user_id, int(course_id),)) != None

        if role_exists:
            sql = '''UPDATE permissions
                     SET role = ?, course_id = ?
                     WHERE user_id = ?'''

            self.execute(sql, (role, course_id, user_id,))
        else:
            sql = '''INSERT INTO permissions (user_id, role, course_id)
                     VALUES (?, ?, ?)'''

            self.execute(sql, (user_id, role, course_id,))

    def remove_permissions(self, course_id, user_id, role):
        sql = '''DELETE FROM permissions
                 WHERE user_id = ?
                   AND role = ?
                   AND (course_id = ? OR course_id IS NULL)'''

        # Admins are not assigned to a particular course.
        if not course_id:
            course_id = "0"

        self.execute(sql, (user_id, role, int(course_id),))

    def add_admin_permissions(self, user_id):
        self.add_permissions(None, user_id, "administrator")

    def get_user_count(self):
        sql = '''SELECT COUNT(*) AS count
                 FROM users'''

        return self.fetchone(sql)["count"]

    def course_exists(self, course_id):
        sql = '''SELECT COUNT(*) AS count
                 FROM courses
                 WHERE course_id = ?'''

        if self.fetchone(sql, (course_id,)):
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

        for course in self.fetchall(sql, (user_id,)):
            course_basics = {"id": course["course_id"], "title": course["title"]}
            courses.append([course["course_id"], course_basics])
        return courses

    def get_course_ids(self):
        sql = '''SELECT course_id
                 FROM courses'''

        return [course[0] for course in self.fetchall(sql)]

    def get_assignment_ids(self, course_id):
        if not course_id:
            return []

        sql = '''SELECT assignment_id
                 FROM assignments
                 WHERE course_id = ?'''

        return [assignment[0] for assignment in self.fetchall(sql, (int(course_id),))]

    def get_exercise_ids(self, course_id, assignment_id):
        if not assignment_id:
            return []

        sql = '''SELECT exercise_id
                 FROM exercises
                 WHERE course_id = ?
                   AND assignment_id = ?'''

        return [exercise[0] for exercise in self.fetchall(sql, (int(course_id), int(assignment_id),))]

    def get_courses(self, show_hidden=True):
        courses = []

        sql = '''SELECT course_id, title, visible, introduction
                 FROM courses
                 ORDER BY title'''

        for course in self.fetchall(sql):
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

        for row in self.fetchall(sql, (course_id,)):
            if row["assignment_visible"] or show_hidden:
                course_basics = {"id": row["course_id"], "title": row["course_title"], "visible": bool(row["course_visible"]), "exists": True}
                assignment_basics = {"id": row["assignment_id"], "title": row["assignment_title"], "visible": row["assignment_visible"], "start_date": row["start_date"], "due_date": row["due_date"], "exists": False, "course": course_basics}
                assignments.append([row["assignment_id"], assignment_basics])

        return assignments

    def get_exercises(self, course_id, assignment_id, show_hidden=True):
        exercises = []

        sql = '''SELECT exercise_id, title, visible
                 FROM exercises
                 WHERE course_id = ?
                   AND assignment_id = ?
                 ORDER BY title'''

        for exercise in self.fetchall(sql, (course_id, assignment_id,)):
            if exercise["visible"] or show_hidden:
                assignment_basics = self.get_assignment_basics(course_id, assignment_id)
                exercise_basics = {"id": exercise["exercise_id"], "title": exercise["title"], "visible": exercise["visible"], "exists": True, "assignment": assignment_basics}
                exercises.append([exercise["exercise_id"], exercise_basics, course_id, assignment_id])

        return exercises

    def get_available_courses(self, user_id):
        available_courses = []

        sql = '''SELECT course_id, title, introduction, passcode
                 FROM courses
                 WHERE course_id NOT IN
                 (
                    SELECT course_id
                    FROM course_registrations
                    WHERE user_id = ?
                 )
                 ORDER BY title'''

        for course in self.fetchall(sql, (user_id,)):
            course_basics = {"id": course["course_id"], "title": course["title"], "introduction": course["introduction"], "passcode": course["passcode"]}
            available_courses.append([course["course_id"], course_basics])

        return available_courses

    def get_registered_courses(self, user_id):
        registered_courses = []

        sql = '''SELECT r.course_id, c.title
                 FROM course_registrations r
                 INNER JOIN courses c
                   ON r.course_id = c.course_id
                 WHERE r.user_id = ?'''

        for course in self.fetchall(sql, (user_id,)):
            course_basics = {"id": course["course_id"], "title": course["title"]}
            registered_courses.append([course["course_id"], course_basics])

        return registered_courses

    def get_registered_students(self, course_id):
        registered_students = []

        sql = '''SELECT r.user_id, u.name
                 FROM course_registrations r
                 INNER JOIN users u
                   ON r.user_id = u.user_id
                 WHERE r.course_id = ?'''

        for student in self.fetchall(sql, (course_id,)):
            student_info = {"id": student["user_id"], "name": student["name"]}
            registered_students.append([student["user_id"], student_info])

        return registered_students

    # Gets whether or not a student has passed each assignment in the course.
    def get_assignment_statuses(self, course_id, user_id):
        sql = '''SELECT assignment_id,
                        title,
                        start_date,
                        due_date,
                        SUM(passed) AS num_passed,
                        COUNT(assignment_id) AS num_exercises,
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
                   FROM exercises e
                   LEFT JOIN submissions s
                     ON e.course_id = s.course_id
                     AND e.assignment_id = s.assignment_id
                     AND e.exercise_id = s.exercise_id
                     AND (s.user_id = ? OR s.user_id IS NULL)
                   INNER JOIN assignments a
                     ON e.course_id = a.course_id
                     AND e.assignment_id = a.assignment_id
                   WHERE e.course_id = ?
                     AND a.visible = 1
                     AND e.visible = 1
                   GROUP BY e.assignment_id, e.exercise_id
                 )
                 GROUP BY assignment_id, title
                 ORDER BY title'''

        assignment_statuses = []
        for row in self.fetchall(sql, (user_id, int(course_id),)):
            assignment_dict = {"id": row["assignment_id"], "title": row["title"], "start_date": row["start_date"], "due_date": row["due_date"], "passed": row["passed_all"], "in_progress": row["in_progress"], "num_passed": row["num_passed"], "num_exercises": row["num_exercises"], "has_timer": row["has_timer"], "hour_timer": row["hour_timer"], "minute_timer": row["minute_timer"]}
            assignment_statuses.append([row["assignment_id"], assignment_dict])

        return assignment_statuses

    # Gets the number of submissions a student has made for each exercise
    # in an assignment and whether or not they have passed the exercise.
    def get_exercise_statuses(self, course_id, assignment_id, user_id, show_hidden=True):
        # This happens when you are creating a new assignment.
        if not assignment_id:
            return []

        sql = '''SELECT e.exercise_id,
                        e.title,
                        IFNULL(MAX(s.passed), 0) AS passed,
                        COUNT(s.submission_id) AS num_submissions,
                        COUNT(s.submission_id) > 0 AND IFNULL(MAX(s.passed), 0) = 0 AS in_progress,
                        IFNULL(sc.score, 0) as score
                 FROM exercises e
                 LEFT JOIN submissions s
                   ON e.course_id = s.course_id
                   AND e.assignment_id = s.assignment_id
                   AND e.exercise_id = s.exercise_id
                   AND s.user_id = ?
                 LEFT JOIN scores sc
                   ON e.course_id = sc.course_id
                   AND e.assignment_id = sc.assignment_id
                   AND e.exercise_id = sc.exercise_id
                   AND (sc.user_id = ? OR sc.user_id IS NULL)
                 WHERE e.course_id = ?
                   AND e.assignment_id = ?
                   AND e.visible = 1
                 GROUP BY e.assignment_id, e.exercise_id
                 ORDER BY e.title'''

        exercise_statuses = []
        for row in self.fetchall(sql, (user_id, user_id, int(course_id), int(assignment_id),)):
            exercise_dict = {"id": row["exercise_id"], "title": row["title"], "passed": row["passed"], "num_submissions": row["num_submissions"], "in_progress": row["in_progress"], "score": row["score"]}
            exercise_statuses.append([row["exercise_id"], exercise_dict])

        return exercise_statuses

    def get_course_scores(self, course_id):
        scores = {}

        sql = assignment_summary_course(course_id)

        for row in self.fetchall(sql):
            scores_dict = {"assignment_id": row["assignment_id"], "title": row["title"], "num_students_completed": row["num_students_completed"], "num_students": row["num_students"], "avg_score": row["avg_score"]}
            scores[row["assignment_id"]] = scores_dict

        return scores

    # Gets all users who have submitted on a particular assignment
    # and creates a list of their average scores for the assignment.
    def get_assignment_scores(self, course_id, assignment_id):
        scores = []

        sql = '''SELECT u.name, s.user_id, (SUM(s.score) / b.num_exercises) AS percent_passed
                 FROM scores s
                 INNER JOIN users u
                   ON s.user_id = u.user_id
                 INNER JOIN (
                   SELECT COUNT(DISTINCT exercise_id) AS num_exercises
                   FROM exercises
                   WHERE course_id = ?
                     AND assignment_id = ?
                     AND visible = 1
                  ) b
                 WHERE s.course_id = ?
                   AND s.assignment_id = ?
                   AND s.user_id NOT IN
                   (
                    SELECT user_id
                    FROM permissions
                    WHERE course_id = 0 OR course_id = ?
                   )
                   AND s.exercise_id NOT IN
				   (
				    SELECT exercise_id
					FROM exercises
					WHERE course_id = ?
					  AND assignment_id = ?
					  AND visible = 0
				   )
                 GROUP BY s.course_id, s.assignment_id, s.user_id
                 ORDER BY u.family_name, u.given_name'''

        for user in self.fetchall(sql, (int(course_id), int(assignment_id), int(course_id), int(assignment_id), int(course_id), int(course_id), int(assignment_id),)):
            scores_dict = {"name": user["name"], "user_id": user["user_id"], "percent_passed": user["percent_passed"]}
            scores.append([user["user_id"], scores_dict])

        return scores

    def get_exercise_scores(self, course_id, assignment_id, exercise_id):
        scores = []

        sql = '''SELECT u.name, s.user_id, sc.score, COUNT(s.submission_id) AS num_submissions
                 FROM submissions s
                 INNER JOIN users u
                   ON u.user_id = s.user_id
                 INNER JOIN scores sc
                 ON sc.course_id = s.course_id
                   AND sc.assignment_id = s.assignment_id
                   AND sc.exercise_id = s.exercise_id
                   AND sc.user_id = s.user_id
                 WHERE s.course_id = ?
                   AND s.assignment_id = ?
                   AND s.exercise_id = ?
                 GROUP BY s.user_id
                 ORDER BY u.family_name, u.given_name'''

        for user in self.fetchall(sql, (int(course_id), int(assignment_id), int(exercise_id),)):
            scores_dict = {"name": user["name"], "user_id": user["user_id"], "num_submissions": user["num_submissions"], "score": user["score"]}
            scores.append([user["user_id"], scores_dict])

        return scores

    def get_exercise_score(self, course_id, assignment_id, exercise_id, user_id):
        sql = '''SELECT score
                 FROM scores
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND exercise_id = ?
                   AND user_id = ?'''

        row = self.fetchone(sql, (int(course_id), int(assignment_id), int(exercise_id), user_id,))
        if row:
            return row["score"]

    def calc_exercise_score(self, assignment_details, passed):
        score = 0
        if passed:
            if assignment_details["due_date"] and assignment_details["due_date"] < datetime.now():
                if assignment_details["allow_late"]:
                    score = 100 * assignment_details["late_percent"]
            else:
                score = 100

        return score

    def save_exercise_score(self, course_id, assignment_id, exercise_id, user_id, new_score):
        score = self.get_exercise_score(course_id, assignment_id, exercise_id, user_id)

        if score != None:
            sql = '''UPDATE scores
                     SET score = ?
                     WHERE course_id = ?
                       AND assignment_id = ?
                       AND exercise_id = ?
                       AND user_id = ?'''

            self.execute(sql, (new_score, course_id, assignment_id, exercise_id, user_id))

        else:
            sql = '''INSERT INTO scores (course_id, assignment_id, exercise_id, user_id, score)
                     VALUES (?, ?, ?, ?, ?)'''

            self.execute(sql, (course_id, assignment_id, exercise_id, user_id, new_score))

    def get_submissions_basic(self, course_id, assignment_id, exercise_id, user_id):
        submissions = []
        sql = '''SELECT submission_id, date, passed
                 FROM submissions
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND exercise_id = ?
                   AND user_id = ?
                 ORDER BY submission_id DESC'''

        for submission in self.fetchall(sql, (int(course_id), int(assignment_id), int(exercise_id), user_id,)):
            submissions.append([submission["submission_id"], submission["date"].strftime("%a, %d %b %Y %H:%M:%S UTC"), submission["passed"]])
        return submissions

    def get_student_submissions(self, course_id, assignment_id, exercise_id, user_id):
        student_submissions = []
        index = 1

        sql = '''SELECT DISTINCT code
                 FROM submissions
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND exercise_id = ?
                   AND passed = 1
                   AND user_id != ?
                 GROUP BY user_id
                 ORDER BY date'''

        for submission in self.fetchall(sql, (course_id, assignment_id, exercise_id, user_id,)):
            student_submissions.append([index, submission["code"]])
            index += 1
        return student_submissions

    def get_help_requests(self, course_id):
        help_requests = []

        sql = '''SELECT r.course_id, a.assignment_id, e.exercise_id, c.title as course_title, a.title as assignment_title, e.title as exercise_title, r.user_id, u.name, r.code, r.text_output, r.image_output, r.student_comment, r.suggestion, r.approved, r.suggester_id, r.approver_id, r.date, r.more_info_needed
                 FROM help_requests r
                 INNER JOIN users u
                   ON r.user_id = u.user_id
                 INNER JOIN courses c
                   ON r.course_id = c.course_id
                 INNER JOIN assignments a
                   ON r.assignment_id = a.assignment_id
                 INNER JOIN exercises e
                   ON r.exercise_id = e.exercise_id
                 WHERE r.course_id = ?
                 ORDER BY r.date DESC'''

        for request in self.fetchall(sql, (course_id,)):
            help_requests.append({"course_id": request["course_id"], "assignment_id": request["assignment_id"], "exercise_id": request["exercise_id"], "course_title": request["course_title"], "assignment_title": request["assignment_title"], "exercise_title": request["exercise_title"], "user_id": request["user_id"], "name": request["name"], "code": request["code"], "text_output": request["text_output"], "image_output": request["image_output"], "student_comment": request["student_comment"], "suggestion": request["suggestion"], "approved": request["approved"], "suggester_id": request["suggester_id"], "approver_id": request["approver_id"], "date": request["date"], "more_info_needed": request["more_info_needed"]})

        return help_requests

    def get_student_help_requests(self, user_id):
        help_requests = []

        sql = '''SELECT r.course_id, a.assignment_id, e.exercise_id, c.title as course_title, a.title as assignment_title, e.title as exercise_title, r.user_id, u.name, r.code, r.text_output, r.image_output, r.student_comment, r.suggestion, r.approved, r.suggester_id, r.approver_id, r.more_info_needed
                 FROM help_requests r
                 INNER JOIN users u
                   ON r.user_id = u.user_id
                 INNER JOIN courses c
                   ON r.course_id = c.course_id
                 INNER JOIN assignments a
                   ON r.assignment_id = a.assignment_id
                 INNER JOIN exercises e
                   ON r.exercise_id = e.exercise_id
                 WHERE r.user_id = ?
                 ORDER BY r.date DESC'''

        for request in self.fetchall(sql, (user_id,)):
            help_requests.append({"course_id": request["course_id"], "assignment_id": request["assignment_id"], "exercise_id": request["exercise_id"], "course_title": request["course_title"], "assignment_title": request["assignment_title"], "exercise_title": request["exercise_title"], "user_id": request["user_id"], "name": request["name"], "code": request["code"], "text_output": request["text_output"], "image_output": request["text_output"], "image_output": request["image_output"], "student_comment": request["student_comment"], "suggestion": request["suggestion"], "approved": request["approved"], "suggester_id": request["suggester_id"], "approver_id": request["approver_id"], "more_info_needed": request["more_info_needed"]})

        return help_requests

    def get_exercise_help_requests(self, course_id, assignment_id, exercise_id, user_id):
        sql = '''SELECT text_output
                 FROM help_requests
                 WHERE course_id = ?
                 AND assignment_id = ?
                 AND exercise_id = ?
                 AND user_id = ?'''
        row = self.fetchone(sql, (course_id, assignment_id, exercise_id, user_id,))
        orig_output = re.sub("#.*", "", row["text_output"])

        sql = '''SELECT r.course_id, r.assignment_id, r.exercise_id, r.user_id, u.name, r.code, r.text_output, r.image_output, r.student_comment, r.suggestion, r.approved, r.suggester_id, r.approver_id, r.more_info_needed
                 FROM help_requests r
                 INNER JOIN users u
                   ON r.user_id = u.user_id
                 WHERE r.course_id = ?
                   AND r.assignment_id = ?
                   AND r.exercise_id = ?
                   AND NOT r.user_id = ?
                 ORDER BY r.date DESC'''

        requests = self.fetchall(sql, (course_id, assignment_id, exercise_id, user_id,))

        nlp = spacy.load('en_core_web_sm')
        orig = nlp(orig_output)
        help_requests = []

        for request in requests:
            curr = nlp(re.sub("#.*", "", request["text_output"]))
            psim = curr.similarity(orig)
            request_info = {"psim": psim, "course_id": request["course_id"], "assignment_id": request["assignment_id"], "exercise_id": request["exercise_id"], "user_id": request["user_id"], "name": request["name"], "code": request["code"], "text_output": request["text_output"], "image_output": request["text_output"], "image_output": request["image_output"], "student_comment": request["student_comment"], "suggestion": request["suggestion"], "approved": request["approved"], "suggester_id": request["suggester_id"], "approver_id": request["approver_id"], "more_info_needed": request["more_info_needed"]}
            help_requests.append(request_info)
                
        return sorted(help_requests, key=lambda x: x["psim"], reverse=True)

    def get_help_request(self, course_id, assignment_id, exercise_id, user_id):
        sql = '''SELECT r.user_id, u.name, r.code, r.text_output, r.image_output, r.student_comment, r.suggestion, r.approved, r.suggester_id, r.approver_id, r.more_info_needed
                 FROM help_requests r
                 INNER JOIN users u
                   ON r.user_id = u.user_id
                 WHERE r.course_id = ?
                   AND r.assignment_id = ?
                   AND r.exercise_id = ?
                   AND r.user_id = ?'''

        request = self.fetchone(sql, (course_id, assignment_id, exercise_id, user_id,))
        if request:
            help_request = {"course_id": course_id, "assignment_id": assignment_id, "exercise_id": exercise_id, "user_id": request["user_id"], "name": request["name"], "code": request["code"], "text_output": request["text_output"], "image_output": request["image_output"], "student_comment": request["student_comment"], "approved": request["approved"], "suggester_id": request["suggester_id"], "approver_id": request["approver_id"], "more_info_needed": request["more_info_needed"]}
            if request["suggestion"]:
                help_request["suggestion"] = request["suggestion"]
            else:
                help_request["suggestion"] = None

            return help_request

    def compare_help_requests(self, course_id, assignment_id, exercise_id, user_id):
        #get the original help request, including its output type
        sql = '''SELECT r.text_output, e.expected_text_output, r.image_output, e.expected_image_output, e.output_type
                 FROM help_requests r
                 INNER JOIN exercises e
                   ON e.course_id = r.course_id
                   AND e.assignment_id = r.assignment_id
                   AND e.exercise_id = r.exercise_id
                 WHERE r.course_id = ?
                   AND r.assignment_id = ?
                   AND r.exercise_id = ?
                   AND r.user_id = ?'''
        row = self.fetchone(sql, (course_id, assignment_id, exercise_id, user_id,))

        #the original output type will be either txt or jpg depending on the output type of the exercise
        orig_output = None

        if row["output_type"] == "img":
            if row["image_output"] != row["expected_image_output"]:
                orig_output = row["image_output"]

        else:
            if row["text_output"] != row["expected_text_output"]:
                orig_output = row["text_output"]

        #get all other help requests in the course that have the same output type
        if orig_output:
                sql = '''SELECT r.course_id, r.assignment_id, r.exercise_id, r.user_id, u.name, r.code, r.text_output, r.image_output, r.student_comment, r.suggestion
                        FROM help_requests r
                        INNER JOIN users u
                          ON r.user_id = u.user_id
                        INNER JOIN exercises e
                          ON e.course_id = r.course_id
                          AND e.assignment_id = r.assignment_id
                          AND e.exercise_id = r.exercise_id
                        WHERE r.course_id = ?
                          AND NOT r.user_id = ?
                          AND e.output_type = ?'''
                requests = self.fetchall(sql, (course_id, user_id, row["output_type"]))
                sim_dict = []

                #jpg output uses the diff_jpg function in helper.py, txt output uses .similarity() from the Spacy module
                if row["output_type"] == "img":
                    for request in requests:
                        diff_image, diff_percent = diff_jpg(orig_output, request["image_output"])
                        if diff_percent < .10:
                            request_info = {"psim": 1 - diff_percent, "course_id": request["course_id"], "assignment_id": request["assignment_id"], "exercise_id": request["exercise_id"], "user_id": request["user_id"], "name": request["name"], "student_comment": request["student_comment"],  "code": request["code"], "text_output": request["text_output"], "suggestion": request["suggestion"]}
                            sim_dict.append(request_info)

                else:
                    nlp = spacy.load('en_core_web_sm')
                    orig = nlp(orig_output)

                    for request in requests:
                        curr = nlp(request["text_output"])
                        psim = curr.similarity(orig)
                        sim = False

                        #these thresholds can be changed in the future
                        if len(orig) < 10 and len(curr) < 10:
                            if psim > .30:
                                sim = True
                        elif len(orig) < 100 and len(curr) < 100:
                            if psim > .50:
                                sim = True
                        elif len(orig) < 200 and len(curr) < 200:
                            if psim > .70:
                                sim = True
                        else:
                            if psim > .90:
                                sim = True

                        if sim:
                            request_info = {"psim": psim, "course_id": request["course_id"], "assignment_id": request["assignment_id"], "exercise_id": request["exercise_id"], "user_id": request["user_id"], "name": request["name"], "student_comment": request["student_comment"],  "code": request["code"], "text_output": request["text_output"], "suggestion": request["suggestion"]}
                            sim_dict.append(request_info)
                            
                #self.test_similarity()
                return sim_dict

    def test_similarity(self):
        #nlp = spacy.load('en_core_web_sm')
        orig = "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"
        orig += "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4gWDdFOrUGrWlMV6mJSJmNOIuUNkCOixW5RFViox2qj3Mh5e6RqH20wpWBinp26M+BVfhtmbdhOqN1zkjETWgzUaBCiRYaRGLuORNhubku4qRXp2lU9B6ptYdHvPQ6vWoTkrDWo2q2WrtKmsv2krHhR4aPcx3bRXQnRWLl/B38jwXS8vir42aPWiPYdanYvW8aK9bS3A5j1asxrwZdsVjlT+HXZrX+ljV/gbi6TWF9q3xoxX5hzM0WTZTYdrzaU+XZBa2HJxZeXc+VdDaiZN62+HDVqJ2tXLtFJ6nFe1Tv3Qvw1q9ZmXx5yTkpmkOe92arDlJqNLwc1/jlChQ0PW76x1wUwwq0Gg4kYuWda1SmJds3Ck6xW5aTjxIDnOakVGRXo5WK5j2o7LJVY5P4KRdC0n9G66KrL0K3MfcPKnUppXJAlJS5ZOLGiqjVcqNY2IqrkiKu5/BFLlt4svffROUIXOG3iy999E5Qhc4beLL330TlCFziv21etmtrV2K67aMiPrENWqs/C3U7HyiZp7r40X/wWDbxZe++icoQucNvFl776JyhC5w28WXvvonKELnDbxZe++icoQucNvFl776JyhC5w28WXvvonKELnDbxZe++icoQucNvFl776JyhC5w28WXvvonKELnEXWL2sxajQ1S7qKqNn3quU/C3E2LH/AMRKbeLL330TlCFzht4svffROUIXOG3iy999E5Qhc4beLL330TlCFzht4svffROUIXOG3iy999E5Qhc4beLL330TlCFzht4svffROUIXOG3iy999E5Qhc4beLL330TlCFzivYe3rZsOx6GyJdtGa5slCRUWfhIqbn/cWHbxZe++icoQucNvFl776JyhC5w28WXvvonKELnDbxZe++icoQucNvFl776JyhC5w28WXvvonKELnDbxZe++icoQucNvFl776JyhC5w28WXvvonKELnGBBvazOz047bdRclk5ZM9nwv78b/EZ+3iy999E5Qhc4beLL330TlCFzht4svffROUIXOG3iy999E5Qhc4beLL330TlCFzht4svffROUIXOG3iy999E5Qhc4beLL330TlCFzht4svffROUIXOIC+r1s19szDWXbRnL16W3En4Sr/bw/8RP7eLL330TlCFzht4svffROUIXOG3iy999E5Qhc4beLL330TlCFzht4svffROUIXOG3iy999E5Qhc4beLL330TlCFzht4svffROUIXOG3iy999E5Qhc4beLL330TlCFziMoV7WY1s9rXdRUznoypnPwu1n/ANxJ7eLL330TlCFzht4svffROUIXOG3iy999E5Qhc4beLL330TlCFzht4svffROUIXOG3iy999E5Qhc4beLL330TlCFzht4svffROUIXOG3iy999E5Qhc4gazetmrdVvOS7aMrWrN5qk/CyT9kn+IntvFl776JyhC5w28WXvvonKELnDbxZe++icoQucNvFl776JyhC5w28WXvvonKELnDbxZe++icoQucNvFl776JyhC5w28WXvvonKELnDbxZe++icoQucfCfvey1kZlEu+i59Zf8A/MIX91f8R8qNe1mJSJFFu6ioqS0JFRZ+F/dT/EZm3iy999E5Qhc4beLL330TlCFzht4svffROUIXOOZXVl65RazceAXYesSU91mernXNjTDIupnEpmWeqq5Z5Ll9CnVAAA1I03tMy9dH+v2fhDgnYEC8cTL5V0SQk5mHFiQZeAj9Rrlhw3MdEc9yRET3bUakN7nLkiIvlcLEHqzUSG2IuB+GsNXIi6jpuTzb/JcqgWTDq9uqzTeINsSuI+EGHklaUasyUOvTMrMyqxoNOWOxJl8NGzrlV7YWuqZNcuaJuL2jecHPfFulWJg71Uq1MYcYmycnbF52sstQ61UEa2Tkq3AakHJ8R3uYbkhNbk5ckRZhi5pkqp9uqo3rhpiFhNauFtkVil3NifWbokHWrJUeahzE9Aeqq10VFhqqw2ORzWIqqiOcrVTPUVUkNM6JN4LaT2jTpQXbETsDRo8zalzVJjF6zJOmoLobYzviYqR5p/0QvjVELT1STGuy4GixV7Cta46dXbnxKfJUW3qbTZpkzHneuzEJz3sZDVVczrbXIjk3Fc9jc83Ied6amFtewZ0aNHK+paQi1CJo+1m3Y1ZbLprKkCDDgsixU/hl1+BBb8X7TPtIe/6Tmk/hBbeilduI1JxAodRgXBbk1K2+ktOw3vn5qZgOhwGMYi6yqjnor0yzY1r1ciaqmboDYZ1nCTRFw5s24pSJK1VKfFqU3Ait1YkF85MRZpIb0/2XNbGa1U7aK1UPTr3wWwcxMqECrYj4TWbdc9KwdjwJmt0GVnosKFrK7Ua+MxytbrOVckXLNVX+JH25o6aPlnVqW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"
        orig += "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"
        orig += "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"
        orig += "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"
        
        curr = "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"
        curr += "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I2bAABRyX6uTFeBt05b42Gy3HrkbZjrQhSrcuTLvQ52eu9v9wi3lwnYNbmV7LKvhhCuzYVbJEk7Ka0rWp6WV0SqqI9GSPRVaqtcmXJkytXyE1l87nyXcbfBl67HdYLmdkbaqV0S0atzs3OSbOzMmdvZcvd3iZZNt2Nb9nRWxYVr0Vo0E6K6KqpKhk0L0Rciq17VVq76L3FIlgXxujep1Sy696bIth1G5GVKUFdFULC5cuRH5jlzV3l3l8hcAFfbng5/pN2kyDvEfoJsPJHGT/b3fz+3Kn1jrY+wwN/teuP/pJZn4qM9iwACPVd8pdd/I4kAAAAFbL4eh1C7XFkAAAARqbhNXrG+o0kgAAAFZd/gK6xdiFmAAADBW8Dn1T9imSHvTPRTYcwAAAVd4uBM1qbFLQAAAAjTcNpvkfsQkgAAAjWj4PqtS/1VPE0GwWIn4xNkfMK77lx6cgGsmMF43mLZrry/g4jZsAA/Fy5N41MvxcO4NJcarxfsHNkNvphIqqhKistxlK3s9mVck/ZVtCurGp/QPbvq1qO7IuRrUbkU+qt24uFWTDDey89NgoureyhksqyKGgrbxWhHC2VsEcr5mwRtilc17pJlRVejGpmJ/WRd6up7x3Xwx3zwM2Wt1orNu+jbw19Xd6ohjWGK06HscCRPY1Mx3YnyzORcmRc5rsidw+YwqMW5lVhtuNdNu5dh2w26ss0NGiRRUb7QqkpKxWNRMjeyxMTLk93f907MvhdW7mDzDRghrbjWDQWM60Z7RsCshoKdsLamh0J8zWvRqJnJHJCxyKu+m/5VLDGLw5YQ8DH6P8A6B4ArxYS92NL0vch06bn9i7Dmdk7FTzd87K/Jlze9OyZd/J9JgnwlXrwhYP7KvhefBda1z7Tr+z9nsWvWRZ6XMnkjbnZ8UbvbNY16ZWJvPTupvr9dutW8TT8/VItpWhU1FI6KWzpYWqqe3dlyJv/ACEiO1axsbWpZEyojUTLv7/+6eUGMZI6XDrfmR8axudbdSqtXup7buHXJ9dgge6PC1cl7WK9W3is1UandVdJj3j153WreJp+fqjdat4mn5+qN1q3iafn6o3WreJp+fqjdat4mn5+qYprTq3vhV1lTNzJM5EXL7Zc1Uydz+PMZd1q3iafn6o3WreJp+fqjdat4mn5+qN1q3iafn6o3WreJp+fqjdat4mn5+qN1q3iafn6o3WreJp+fqjdat4mn5+qRH19Stpx1C2fIj2x5qRb+VU39/uEvdat4mn5+qN1q3iafn6o3WreJp+fqjdat4mn5+qN1q3iafn6o3WreJp+fqjdat4mn5+qN1q3iafn6o3WreJp+fqmGK06ts070sqZyvciqiZfa+1RMnc/1mbdat4mn5+qN1q3iafn6o3WreJp+fqjdat4mn5+qN1q3iafn6o3WreJp+fqjdat4mn5+qN1q3iafn6o3WreJp+fqkOy6+ppqZY4rPknbnquc3Lk9ze7ikzdat4mn5+qN1q3iafn6o3WreJp+fqjdat4mn5+qN1q3iafn6o3WreJp+fqjdat4mn5+qN1q3iafn6pjqLUrJKeVjr"
        curr += "JmYjmORXLlyImTu9w5MtWsaxqJZEyoiImXf3/APdOW61bxNPz9UbrVvE0/P1RutW8TT8/VG61bxNPz9UbrVvE0/P1RutW8TT8/VG61bxNPz9UbrVvE0/P1SFatdUVNO2OagkgRHouc7LkVci73cQm7rVvE0/P1RutW8TT8/VG61bxNPz9UbrVvE0/P1RutW8TT8/VG61bxNPz9UbrVvE0/P1RutW8TT8/VG61bxNPz9UwyWnVuqIZFsqZFYjsjd/K7L/qM261bxNPz9UbrVvE0/P1RutW8TT8/VG61bxNPz9UbrVvE0/P1RutW8TT8/VG61bxNPz9UbrVvE0/P1SPaNrVq2fUpuPP3l/l96v+aeMAO/MR6eSnxg7KligdM5KGtTMb3V/oVPSvdat4mn5+qN1q3iafn6o3WreJp+fqmt2HWrmqsbvFv7NRvgzZryZM7Lv/AN5xfwQ2lAAMdQyaSCSOnmSKVzHIyRW5yMdk3lye7kX3DoS42ALDbg6sBl3LsYwdkw0yTS1Msktx45JqiaR6vkllkWqzpHuVVyuXfyZE7iIfX23gqv4l5bQvNcPDDW3efbUUKWnSVNlx2jTOmjZmJNTskemjvVO6iK5qqiKrVUiy4vdl2ddi61m3NvPXWPbtz6uorrOtyaJlXLLNU52lrURuzUlbNnuVzUVuRUbmqmaiGWkwA2TX3YvjZF+7wVV4bVv4sa2zarYGUrk7C1G0zaeNuckTYc1HMRVcudlcqrlM918Ed4ae+Fl31wi4RZr2113qSaksZiWZHRR0yzNRs070Y5yyzOY1G52VrURXZGpnHZwBX254Of6TdpMg7xH6CbDyRxk/2938/typ9Y62PsMDf7Xrj/6SWZ+KjPYsAAj1XfKXXfyOJAAAABWy+HodQu1xZAAAAEam4TV6xvqNJIAAABWXf4CusXYhZgAAAwVvA59U/Ypkh70z0U2HMAAAFXeLgTNamxS0AAAAI03Dab5H7EJIAAAI1o+D6rUv9VTxNBsFiJ+MTZHzCu+5cenIBrJjBeN5i2a68v4OI2bAAAAAABX254Of6TdpMg7xH6CbDyRxk/2938/typ9Y62PsMDf7Xrj/AOklmfioz2LAAI9V3yl138jiQAAAAVsvh6HULtcWQAAABGpuE1esb6jSSAAAAVl3+ArrF2IWYAAAMFbwOfVP2KZIe9M9FNhzAAABV3i4EzWpsUtAAAACNNw2m+R+xCSAAACNaPg+q1L/AFVPE0GwWIn4xNkfMK77lx6cgGsmMF43mLZrry/g4jZsAAAAAAFfbng5/pN2kyDvEfoJsPJHGT/b3fz+3Kn1jrY+wwN/teuP/pJZn4qM9iwACPVd8pdd/I4kAAAAFbL4eh1C7XFkAAAARqbhNXrG+o0kgAAAFZd/gK6xdiFmAAADBW8Dn1T9imSHvTPRTYcwAAAVd4uBM1qbFLQAAAAjTcNpvkfsQkgAAAjWj4PqtS/1VPE0GwWIn4xNkfMK77lx6cgGsmMF43mLZrry/g4jZsAAAAAAFfbng5/pN2kyDvEfoJsPJHGT/b3fz+3Kn1jrY+wwN/teuP8A6SWZ+KjPYsAAj1XfKXXfyOJAAAABWy+HodQu1xZAAAAEam4TV6xvqNJIAAABWXf4CusXYhZgAAAwVvA59U/Ypkh70z0U2HMAAAFXeLgTNamxS0AAAAI03Dab5H7EJIAAAI1o+D6rUv8AVU8TQbBYifjE2R8wrvuXHpyAayYwXjeYtmuvL+DiNmwAAAAAAV9ueDn+k3aTIO8R+gmw8kcZP9vd/P7cqfWOtj7DA3+164/+klmfioz2LAAI9V3yl138jiQAAAAVsvh6HULtcWQAAABGpuE1esb6jSSAAAAVl3+ArrF2IWYAAAMFbwOfVP2KZIe9M9FNhzAAABV3i4EzWpsUtAAAACNNw2m+R+xCSAADVnGQxwbyYD8Iv6E2Xc6zbTgWggrEnqJ5GPyvVyK3I3e3s3nOrP1kV9f3a2J/tkvQcKj2Ry+lRBJAuDexESRisVUq5d7KmTyGoANgsRPxibI+YV33Lj05ANZMYLxvMWzXXl/BxGzYAAAAAAK+3PBz/SbtJkHeI/QTYeSOMn+3u/n9uVPrHWx9hgb/AGvXH/0ksz8VGexYABHqu+Uuu/kcSAAAACtl8PQ6hdriyAAAAI1Nwmr1jfUaSQAAACsu/wABXWLsQswAAAYK3gc+qfsUyQ96Z6KbDmAAACrvFwJmtTYpaAAAAEabhtN8j9iEkAAHmx7ID+3tv9h0frSmtYANgsRPxibI+YV33Lj05ANZMYLxvMWzXXl/BxGzYAAAAAAK+3PBz/SbtJkHeI/QTYeSOMn+3u/n9uVPrHWxKsq1K+xLUo7asqpdT1tn1EdVTTNRFWOVjkcxyZd7Kioi752n222MX+9K0eQg/LHbbYxf70rR5CD8s2hxF8MWEvCjbd7aa/17Kq2I7PpaR9M2ZkbUjc98iOVMxqd1Gp3fIbegj1XfKXXfyOJAAAABWy+HodQu1xZAAAAEam4TV6xvqNJIAAABWXf4CusXYhZgAAAwVvA59U/Ypkh70z0U2HMAAAFXeLgTNamxS0AAAAI03Dab5H7EJIB0PjpXuvPcnArJbt0berbItBtq0sSVNJMscmY7Pzm5U9xfIaCdsjh6/e3eb/b3jtkcPX727zf7e8+PvVfG9N+LU3bvfb1ba9f2JsOkVcqySZjcuRuVfcTKv/uU4ANgsRPxibI+YV33Lj05ANZMYLxvMWzXXl/BxGzYAAAAAAK+3PBz/SbtJkHeI/QTYeSOMn+3u/n9uVPrHWwANzPY2f8ACG/PzKh9eU3vBHqu+Uuu/kcSAAAACtl8PQ6hdriyAAAAI1Nwmr1jfUaSQAAACsu/wFdYuxCzAAABgreBz6p+xTJD3pnopsOYAAAKu8XAma1NiloAAAARpuG03yP2ISSk/Te5fwvsT6wi6w/Ti5fwvsT6wi6xrzj13mu5auAeWksu8Fm1k+69I7sVPVxyPyJn5VyNVVyHnKAAAbBYifjE2R8wrvuXHpyAayYwXjeYtmuvL+DiNmwAAAAAYHUcL3K5yy5VXKuSV6J/7Ip+aDB5ZuWf0kK2KWKKge9iyZcqd2Vyp3fIqkqGigWFiqsu+1P8s/yfKeS+Mg1GYeb9sblyJblSiZVVV/reVTrcAHfeKdh6uZgKtS8VbfGzLbrI7Xp6eKBLMbG5WrG56uz8+Rm97ZMmTL7psh+sJwIfBW/fJU//ADQ/WE4EPgrfvkqf/mjYG5F6rFwi3QsG+9iU9fBQ203s8MdW9Ula3I9Mjka9yIuVvuKp9PoMHlm5Z/SNBg8s3LP6RoMHlm5Z/SNBg8s3LP6RoMHlm5Z/SNBg8s3LP6RoMHlm5Z/SNBg8s3LP6RoMHlm5Z/SQJKaJLZiiRZM1YVXvjsvdX3cuUn6DB5ZuWf0jQYPLNyz+kaDB5ZuWf0jQYPLNyz+kaDB5ZuWf0jQYPLNyz+kaDB5ZuWf0jQYPLNyz+kaDB5ZuWf0mCCjhdUVLVWXI17UT+lf71P475n0GDyzcs/pGgweWbln9I0GDyzcs/pGgweWbln9I0GDyzcs/pGgweWbln9I0GDyzcs/pGgweWbln9I0GDyzcs/pK+xKaKajVz1ky56p7WRzU7ie4ilhoMHlm5Z/SNBg8s3LP6RoMHlm5Z/SNBg8s3LP6RoMHlm5Z/SNBg8s3LP6RoMHlm5Z/SNBg8s3LP6TFV0cDaSZyLLlSNyplmevufKc4qKBYmKqy77U/yz+k5aDB5ZuWf0jQYPLNyz+kaDB5ZuWf0jQYPLNyz+kaDB5ZuWf0jQYPLNyz+kaDB5ZuWf0jQYPLNyz+krrdpooaRjmLJlWRE9tI53uL5VLHQYPLNyz+kaDB5ZuWf0jQYPLNyz+kaDB5ZuWf0jQYPLNyz+kaDB5ZuWf0jQYPLNyz+kaDB5ZuWf0jQYPLNyz+kwS0cKVdO1FlyOR+X+lf5E/iZ9Bg8s3LP6TxSrOFz6x20wgAAAGwGIvG2XGHslj87JoFd/VcrV7y73UPTPQYPLNyz+kaDB5ZuWf0jQYPLNyz+k1ow+wRw43mLbmK/fmvJlznud/4OLyqbPgAAAAAAr7c8HP9Ju0mQd4j9BNh5I4yf7e7+f25U+sdbAAAHo7i/Yf8DN2cC1ybAt/CLZFDaNn0qMqqeWRUfE7LJvLvfxT/ANzsztocX3969hcs7oJlkYxeBC3rVo7EsbCVY1XX187Kamp4pFV8sr3I1rUTJ3VVUQ7GAAAK2Xw9DqF2uLIAAAAjU3CavWN9RpJAAAAKy7/AV1i7ELMAAAGCt4HPqn7FMkPemeimw5gAAAq7xcCZrU2KWgAAAOlMNWNfg/wFXqpbo3qsO8FZV1dnx2iySz4YHxpG+SSNEVZJWLnZYne5kyKm+ddyeyJYHH1EMqXTvnkjR2X+9aXLvp84Mv6xfA18Er6f7LS/8weeM8iSzyStRUR71cmX+KnAAAAA2CxE/GJsj5hXfcuPTkA1kxgvG8xbNdeX8HEbNgAAAAAAr7c8HP8ASbtJkHeI/QTYeSOMn+3u/n9uVPrHWwAAAB9VgovJZtzsJt1b2WwsqUFj2xSV1T2Jmc/sUcrXOzU91ciLvHoB2/mAHzt4vq1OuO38wA+dvF9Wp1zsjA7h/uBhy3X/AEGdaK7iaPpWl03Yu/dkzM3fXL3p2X/UdkgArZfD0OoXa4sgAAACNTcJq9Y31GkkAAAArLv8BXWLsQswAAAYK3gc+qfsUyQ96Z6KbDmAAACrvFwJmtTYpaAAEC3LfsK7FmS21eS2qGyrPgVqS1dbUMghjznI1uc96o1MrlREyrvqqIfK/wB3bAj++G5P1/SfmD+7tgR/fDcn6/pPzDQ3HxvZda+OF+ybTujeSy7bo4rt08D6izqyOpjbIlTUuViujVURyI5q5O7kcnlNbwAAAAAbBYifjE2R8wrvuXHpyAayYwXjeYtmuvL+DiNmwAAAAAAV9ueDn+k3aTIO8R+gmw8kcZP9vd/P7cqfWOtgAAAAAd3YtOMsuLut41S5aXg/SDRP/iOi9g7B2b/6T87O7N/DJm+7l3u7v1ljv3Lp9ov+lH6yx37l0+0X/SnWNVj74fJKmaSkrbHhgdI5Yo3Wex7mMVd5qu3s5UTey5Ey+RDF2+mMJxnYn1YzpPvsX/G0wxYSMNd2Lq3mr7MfQWjLLDOkNC2NytbDI9Mip3N9qG+gAAABGpuE1esb6jSSAAAAVl3+ArrF2IWYAAAMFbwOfVP2KZIe9M9FNhzAAABV3i4EzWpsUr704SMH9x6iCkvlfWxLEmqWLJDHaFdHA6RqLkVWo9Uypl8hSdsDgM/e9c/65g6w7YHAZ+965/1zB1jo+1/ZEMG1l2tW2ZFc2261lJUSQNqaeaB0U6McrUkYudvtdkyovkVCJ+sewdfu/vHykHWOu8P+OnczC/gptjB/ZF0Laoaq0nUzmT1L4ljb2KojlXLmuVd9GKnyqahAAAAAAAGwWIn4xNkfMK77lx6cgGsmMF43mLZrry/g4jZsAAAAAAFfbng5/pN2kyDvEfoJsPJHGT/b3fz+3Kn1jrYAAAAAAAAnWJbts3atSnty71q1Vm2hSqroKqlldFLEqoqKrXNyKm8qpveU+x7YHDn+969/1xP1h2wOHP8Ae9e/64n6x3zi6Y6tJg+sS16PDBaV9Lz1tXVslo5myMq0hiRmRW5Zpmq3K7fyIiodufrFsCnwWvv/ALFSf8yP1i2BT4LX3/2Kk/5k/P1i+Bb4K32/2Ok/5kfrF8C3wVvt/sdJ/wAyfHYUvZC7LrbuwxYH7JtigtpKtjpZLaoIHQLTZj85qZkzlzs5Y1Te7iLvnVXb84wP/wDMsH6sTrHBmPph+Y98jauwcsiorv8As1PcTJ77+B2pgs9kMoqKwamLDBY9qWha61jnU8li0UDIW02YzNa5HytXPz0kXuZMiofZfrGMDfwRvn/stL/zBxk9kZwPpG5Ybn3xdIjVzWup6VqKvuIq9nXIn8cinx36y3/7K/8A7H/0o/WW/wD2V/8A2P8A6UL7JavuYFk+0f8A0p+frLH/ALl0+0X/AEo/WWP/AHLp9ov+lNlcX/DGuHO4H6cLd3cT+/ZqPRdL0nvaNXOz8xndzu5k9zun293+ArrF2IQMI146u52D2897rPhhmqrDsattKCOZFWN8kMD5GtdkVFzVVqIuRUXJ7por+sawtfAy6PJVP5w/WNYWvgZdHkqn84trteyP3whr3uvhg9seroliVGMs2aWnlSXKmRVdI6RFbkzt7Ny5VTf3si/S/rKLG/dJW/XDPyR+sosb90lb9cM/JPuLs4/2BW07GgrbystOxLQer0lom076pI0Ryo1eyNaiOyoiL3N7LkLTt7sXfj61vquXoMtNjt4AraqIrGoLctNamve2lhR9myNasj1zW5XLvImVU31O74resPsTP+2aH+qn/iGeT5Tlu9YfHND/ALQzpOpMPWNFdbAU+xGVdjT29u0lSrVoaqNOw9h7HlzsuXu9l3vRU6m/WRXK/drbf+2RdA/WRXK/drbf+2RdB3VcDGdwQX0ujZ957Svzdu7lTXNkV9mWlblLHU0+bI5iI9qvRUVUajk3u45D6H+7pgS/fDcj7QUn5h1pjIYc7guwJ3oS4WGGwFt/sEOhbkXgh0zO0iPO7H2KTPy5udlye5l9w8/P7t+Gn9719fr+r/MOMmGrDJM3NlwtXzeiLlyOt6qVMvKFHeO+N7r4TQ1N7r02vbc1O1WQyWjXS1Lo2quVUasjlVEy+4hUAAAAAAAAAA2CxE/GJsj5hXfcuPTkA1kxgvG8xbNdeX8HEbNgAAAAAAr7c8HP9Ju0mQd4j9BNh5I4yf7e7+f25U+sdbAAAAAAAAAAAAAAAAAA21xY8bzB/gTwZ/oVeW794ays3Qnq+yUMUDosx6MREyvlauX2q+4dnWX7IbgjoqZYZbo3vcquV2VtPS5Pc/8ArlThGx9sFd8cHt6Lo2ddW9cNVbljVtmwSTQUyRskmgfG1zlSZVzUVyKuRFXJ7imiQAAAAAAAAAAAAAAAAAABsFiJ+MTZHzCu+5cenIBrJjBeN5i2a68v4OI2bAAAAAABX254Of6TdpMg7xH6CbDyRxk/2938/typ9Y62AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABsFiJ+MTZHzCu+5cenIBrJjBeN5i2a68v4OI2bAAAAPxVREVVVERN9VUqLAvjdG9Tqll1702RbDqNyMqUoK6KoWFy5ciPzHLmrvLvL5C4AK+3PBz/SbtJkHeI/QTYeSOMn+3u/n9uVPrHWwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANgsRPxibI+YV33Lj05ANZMYLxvMWzXXl/BxGzYAAAB1LjUVlZS4D7cpqOplpktSps6yp5o3Zqsp6qtggm3/cyxyPb/wDkUd8Lq3cweYaMENbcawaCxnWjPaNgVkNBTthbU0OhPma16NRM5I5IWORV303/ACqWGMXhywh4GP0f/QPAFeLCXuxpel7kOnTc/sXYczsnYqebvnZX5Mub3p2TLv5PpME+Eq9eELB/ZV8Lz4LrWufadf2fs9i16yLPS5k8kbc7Pijd7ZrGvTKxN56d1N9frt1q3iafn6pFtK0KmopHRS2dLC1VT27suRN/5CRHatY2NrUsiZURqJl39/8A3Tz9wzYqmHm+mFa9V67DuP2Wz7VtSeqpnuroGq6NzsqLkc9FT/WiKfGdpbjG/AJPrCm64XEtxjkTeuCi/wDqFN+YO0txjfgEn1hTdcdpbjG/AJPrCm647S3GOy5P0BT5d0Kb8wdpbjG/AJPrCm647S3GN+ASfWFN1zj2l+MYmTOuG1quXIiLaNNvryn8Dl2luMb8Ak+sKbrn4uJdjHImVLgIu+nctGm/MP3tLcY34BJ9YU3XHaW4xvwCT6wpuufnaW4x2VU/QFMmTu7o035h+9pbjG/AJPrCm647S3GN+ASfWFN1z8TEtxjlRFW4KJ/BbQpvzD97S3GN+ASfWFN1zguJljFJIkS3FZnqmVG7pU2XJ5cnZDn2luMb8Ak+sKbrjtLcY34BJ9YU3XHaW4x2XJ+gKfLuhTfmDtLcY34BJ9YU3XHaW4xvwCT6wpuufiYluMcqIq3BRFVO4to029/xD97S3GN+ASfWFN1z8XEuxjkVES4CLlXjGm3v+IfvaW4xvwCT6wpuufiYl+MW5ValxGqrd5US0abe/wB8JiW4xyqv/cFEyf8AmFNv/wDEP3tLcY34BJ9YU3XC4luMcif4BIv/AKhTdcdpbjHfAJPrCm647S3GN+ASfWFN1wuJbjHZU/7gpv8A/mFNvf8AEHaW4xvwCT6wpuuO0txjfgEn1hTdc/ExLcY5VX/uCiZP/Mabf/4h+R4mOMTM3OiuNG9uXJlbaVMqfeH67EuxjkaqpcBHKiZciWjTZV/4h+9pbjG/AJPrCm647S3GN+ASfWFN1z87S3GOyon6Ap8u6NN+YfvaW4xvwCT6wpuuO0txjfgEn1hTdcJiW4xy/wDyCif+oU35g7S3GN+ASfWFN1z8fiX4xjGq91w25GplX/tGmT//AEP1MS3GNVMqXDaqL/5jTdcdpbjG/AJPrCm65+dpbjHZcn6Ap8u6FN+YfvaW4xvwCT6wpuuO0txjfgEn1hTdc/ExLsY5UyrcBE317to035h+9pbjG/AJPrCm65+LiW4xyJvXBRd/3LRpvzD97S3GN+ASfWFN1zjJiZYxMLc6a48bEVcmV1pUyJl5Q/e0txjsuT9AU+XdCm/MP3tLcY34BJ9YU3XHaW4xvwCT6wpuuExLcY5UyrcFE/8AUKb8wdpbjG/AJPrCm64XEtxjk/8AkFF/9QpvzB2luMb8Ak+sKbrjtLcY34BJ9YU3XPztLcY7KqfoCmTJ3d0ab8wLiX4xaORq3Eaiu7ibo02Vf98/e0txjfgEn1hTdc/G4l2McrUVbgI1VTuLaNNlT/iH72luMb8Ak+sKbrn4uJbjHJk/7gouX/zCm3v+IfvaW4xvwCT6wpuuO0txjfgEn1hTdcdpbjHZV/7gp9YU35g7S3GN+ASfWFN1x2luMd8Ak+sKbrnBuJljEuesSXGZ2REyqzdKmzk+VOyHPtLcY34BJ9YU3XO28VrFyw0YLMMNn3wvbcx1PZsFLVRSSNrIZFRz4la32rHKvd/gbubrVvE0/P1RutW8TT8/VG61bxNPz9U1uw61c1Vjd4t/ZqN8GbNeTJnZd/8AvOL+CG0oAAABQX9uVYuEa59q3JvC2VaC1oFgldE7NkjXKjmSMXIuR7XI1zVyLkVqHyF18Ed4ae+Fl31wi4RZr2113qSaksZiWZHRR0yzNRs070Y5yyzOY1G52VrURXZGpnHZwBX254Of6TdpMg7xH6CbDIAAACPVd8pdd/I4kAAAAFbL4eh1C7XFkAAAARqbhNXrG+o0kgAAAFZd/gK6xdiFmAAADBW8Dn1T9imSHvTPRTYcwAAAVd4uBM1qbFLQAAAAjTcNpvkfsQkgAAAFXT/4QVOqTY0tAADWTGC8bzFs115fwcRs2AAAAAACvtzwc/0m7SZB3iP0E2GQAAAEeq75S67+RxIAAAAK2Xw9DqF2uLIAAAAjU3CavWN9RpJAAAAKy7/AV1i7ELMAAAGCt4HPqn7FMkPemeimw5gAAAq7xcCZrU2KWgAAABGm4bTfI/YhJAAAAKun/wAIKnVJsaWgABrJjBeN5i2a68v4OI2bAAAAABrreXDrjTWVeK1LMsPE4qbWs2krJoKOvS+VJElXA16oybMWNVZntRHZqqqplye4VvbCY3XxIar7b0n5R8rhNxvcYfB1dCpvVf7FAmsWxqaSJk1ZJfGnkRjnvRrEzWQq5crlRO4fQ2ZjIY19o2bSWhQYk9TNTVMEc0MiX2pER8bmorXZFiyplRUXfJPbCY3XxIar7b0n5Q7YTG6+JDVfbek/KHbC"
        curr += "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"
        diff_image, diff_percent = diff_jpg(orig, curr)
        print(diff_percent)

    def get_same_suggestion(self, help_request):
        sql = '''SELECT r.suggestion, e.output_type, r.text_output, r.image_output
                 FROM help_requests r
                 INNER JOIN exercises e
                   ON e.exercise_id = r.exercise_id
                 WHERE r.course_id = ?
                   AND r.suggestion NOT NULL
                   AND e.output_type = (
                       SELECT output_type
                       FROM exercises
                       WHERE exercise_id = ?
                   )'''
        
        matches = self.fetchall(sql, (help_request["course_id"], help_request["exercise_id"]))
        for match in matches:
            if match["output_type"] == "img":
                if match["image_output"] == help_request["image_output"]:
                    return match["suggestion"]
            else:
                if match["text_output"] == help_request["text_output"]:
                    return match["suggestion"]            

    def get_exercise_submissions(self, course_id, assignment_id, exercise_id):
        exercise_submissions = []

        sql = '''SELECT s.code, u.user_id, u.name, sc.score, s.passed
                 FROM submissions s
                 INNER JOIN users u
                   ON s.user_id = u.user_id
                 INNER JOIN scores sc
                   ON s.user_id = sc.user_id
                   AND s.course_id = sc.course_id
				   AND s.assignment_id = sc.assignment_id
				   AND s.exercise_id = sc.exercise_id
                 WHERE s.course_id = ?
                   AND s.assignment_id = ?
                   AND s.exercise_id = ?
                   AND s.user_id IN
                   (
                      SELECT user_id
                      FROM course_registrations
                      WHERE course_id = ?
                   )
                 GROUP BY s.user_id
                 ORDER BY u.family_name, u.given_name'''

        for submission in self.fetchall(sql, (course_id, assignment_id, exercise_id, course_id,)):
            submission_info = {"user_id": submission["user_id"], "name": submission["name"], "code": submission["code"], "score": submission["score"], "passed": submission["passed"]}
            exercise_submissions.append([submission["user_id"], submission_info])

        return exercise_submissions

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

    def specify_assignment_details(self, assignment_details, introduction, date_created, date_updated, start_date, due_date, allow_late, late_percent, view_answer_late, enable_help_requests, has_timer, hour_timer, minute_timer):
        assignment_details["introduction"] = introduction
        assignment_details["date_updated"] = date_updated
        assignment_details["start_date"] = start_date
        assignment_details["due_date"] = due_date
        assignment_details["allow_late"] = allow_late
        assignment_details["late_percent"] = late_percent
        assignment_details["view_answer_late"] = view_answer_late
        assignment_details["enable_help_requests"] = enable_help_requests
        assignment_details["has_timer"] = has_timer
        assignment_details["hour_timer"] = hour_timer
        assignment_details["minute_timer"] = minute_timer

        if assignment_details["date_created"]:
            assignment_details["date_created"] = date_created
        else:
            assignment_details["date_created"] = date_updated

    def specify_exercise_basics(self, exercise_basics, title, visible):
        exercise_basics["title"] = title
        exercise_basics["visible"] = visible

    def specify_exercise_details(self, exercise_details, instructions, back_end, output_type, answer_code, answer_description, hint, max_submissions, starter_code, test_code, credit, data_files, show_expected, show_test_code, show_answer, show_student_submissions, expected_text_output, expected_image_output, date_created, date_updated):
        exercise_details["instructions"] = instructions
        exercise_details["back_end"] = back_end
        exercise_details["output_type"] = output_type
        exercise_details["answer_code"] = answer_code
        exercise_details["answer_description"] = answer_description
        exercise_details["hint"] = hint
        exercise_details["max_submissions"] = max_submissions
        exercise_details["starter_code"] = starter_code
        exercise_details["test_code"] = test_code
        exercise_details["credit"] = credit
        exercise_details["data_files"] = data_files
        exercise_details["show_expected"] = show_expected
        exercise_details["show_test_code"] = show_test_code
        exercise_details["show_answer"] = show_answer
        exercise_details["show_student_submissions"] = show_student_submissions
        exercise_details["expected_text_output"] = expected_text_output
        exercise_details["expected_image_output"] = expected_image_output
        exercise_details["date_updated"] = date_updated

        if exercise_details["date_created"]:
            exercise_details["date_created"] = date_created
        else:
            exercise_details["date_created"] = date_updated

    def get_course_basics(self, course_id):
        if not course_id:
            return {"id": "", "title": "", "visible": True, "exists": False}


        sql = '''SELECT course_id, title, visible
                 FROM courses
                 WHERE course_id = ?'''

        row = self.fetchone(sql, (int(course_id),))

        return {"id": row["course_id"], "title": row["title"], "visible": bool(row["visible"]), "exists": True}

    def get_assignment_basics(self, course_id, assignment_id):
        course_basics = self.get_course_basics(course_id)

        if not assignment_id:
            return {"id": "", "title": "", "visible": True, "exists": False, "course": course_basics}

        sql = '''SELECT assignment_id, title, visible
                 FROM assignments
                 WHERE course_id = ?
                   AND assignment_id = ?'''

        row = self.fetchone(sql, (int(course_id), int(assignment_id),))
        if row is None:
            return {"id": "", "title": "", "visible": True, "exists": False, "course": course_basics}
        else:
            return {"id": row["assignment_id"], "title": row["title"], "visible": bool(row["visible"]), "exists": True, "course": course_basics}

    def get_exercise_basics(self, course_id, assignment_id, exercise_id):
        assignment_basics = self.get_assignment_basics(course_id, assignment_id)

        if not exercise_id:
            return {"id": "", "title": "", "visible": True, "exists": False, "assignment": assignment_basics}

        sql = '''SELECT exercise_id, title, visible
                 FROM exercises
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND exercise_id = ?'''

        row = self.fetchone(sql, (int(course_id), int(assignment_id), int(exercise_id),))
        if row is None:
            return {"id": "", "title": "", "visible": True, "exists": False, "assignment": assignment_basics}
        else:
            return {"id": row["exercise_id"], "title": row["title"], "visible": bool(row["visible"]), "exists": True, "assignment": assignment_basics}

    def get_next_prev_exercises(self, course, assignment, exercise, exercises):
        prev_exercise = None
        next_exercise = None

        if len(exercises) > 0 and exercise:
            this_exercise = [i for i in range(len(exercises)) if exercises[i][0] == int(exercise)]
            if len(this_exercise) > 0:
                this_exercise_index = [i for i in range(len(exercises)) if exercises[i][0] == int(exercise)][0]

                if len(exercises) >= 2 and this_exercise_index != 0:
                    prev_exercise = exercises[this_exercise_index - 1][1]

                if len(exercises) >= 2 and this_exercise_index != (len(exercises) - 1):
                    next_exercise = exercises[this_exercise_index + 1][1]

        return {"previous": prev_exercise, "next": next_exercise}

    def get_num_submissions(self, course, assignment, exercise, user):
        sql = '''SELECT COUNT(*)
                 FROM submissions
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND exercise_id = ?
                   AND user_id = ?'''

        return self.fetchone(sql, (int(course), int(assignment), int(exercise), user,))[0]

    def get_next_submission_id(self, course, assignment, exercise, user):
        return self.get_num_submissions(course, assignment, exercise, user) + 1

    def get_last_submission(self, course, assignment, exercise, user):
        last_submission_id = self.get_num_submissions(course, assignment, exercise, user)

        if last_submission_id > 0:
            return self.get_submission_info(course, assignment, exercise, user, last_submission_id)

    def get_submission_info(self, course, assignment, exercise, user, submission):
        sql = '''SELECT code, text_output, image_output, passed, date
                 FROM submissions
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND exercise_id = ?
                   AND user_id = ?
                   AND submission_id = ?'''

        row = self.fetchone(sql, (int(course), int(assignment), int(exercise), user, int(submission),))

        return {"id": submission, "code": row["code"], "text_output": row["text_output"], "image_output": row["image_output"], "passed": row["passed"], "date": row["date"].strftime("%m/%d/%Y, %I:%M:%S %p"), "exists": True}

    def get_course_details(self, course, format_output=False):
        if not course:
            return {"introduction": "", "passcode": None, "date_created": None, "date_updated": None}

        sql = '''SELECT introduction, passcode, date_created, date_updated
                 FROM courses
                 WHERE course_id = ?'''

        row = self.fetchone(sql, (int(course),))

        course_dict = {"introduction": row["introduction"], "passcode": row["passcode"], "date_created": row["date_created"], "date_updated": row["date_updated"]}
        if format_output:
            course_dict["introduction"] = convert_markdown_to_html(course_dict["introduction"])

        return course_dict

    def get_assignment_details(self, course, assignment, format_output=False):
        if not assignment:
            return {"introduction": "", "date_created": None, "date_updated": None, "start_date": None, "due_date": None, "allow_late": False, "late_percent": None, "view_answer_late": False, "enable_help_requests": 1, "has_timer": 0, "hour_timer": None, "minute_timer": None}

        sql = '''SELECT introduction, date_created, date_updated, start_date, due_date, allow_late, late_percent, view_answer_late, enable_help_requests, has_timer, hour_timer, minute_timer
                 FROM assignments
                 WHERE course_id = ?
                   AND assignment_id = ?'''

        row = self.fetchone(sql, (int(course), int(assignment),))

        assignment_dict = {"introduction": row["introduction"], "date_created": row["date_created"], "date_updated": row["date_updated"], "start_date": row["start_date"], "due_date": row["due_date"], "allow_late": row["allow_late"], "late_percent": row["late_percent"], "view_answer_late": row["view_answer_late"], "enable_help_requests": row["enable_help_requests"], "has_timer": row["has_timer"], "hour_timer": row["hour_timer"], "minute_timer": row["minute_timer"]}
        if format_output:
            assignment_dict["introduction"] = convert_markdown_to_html(assignment_dict["introduction"])

        return assignment_dict

    def get_exercise_details(self, course, assignment, exercise, format_content=False):
        if not exercise:
            return {"instructions": "", "back_end": "python", "output_type": "txt", "answer_code": "", "answer_description": "", "hint": "",
            "max_submissions": 0, "starter_code": "", "test_code": "", "credit": "", "data_files": "", "show_expected": True, "show_test_code": True, "show_answer": True,
            "show_student_submissions": False, "expected_text_output": "", "expected_image_output": "", "data_files": "", "date_created": None, "date_updated": None}

        sql = '''SELECT instructions, back_end, output_type, answer_code, answer_description, hint, max_submissions, starter_code, test_code, credit, data_files, show_expected, show_test_code, show_answer, show_student_submissions, expected_text_output, expected_image_output, data_files, date_created, date_updated
                 FROM exercises
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND exercise_id = ?'''

        row = self.fetchone(sql, (int(course), int(assignment), int(exercise),))

        exercise_dict = {"instructions": row["instructions"], "back_end": row["back_end"], "output_type": row["output_type"], "answer_code": row["answer_code"], "answer_description": row["answer_description"], "hint": row["hint"], "max_submissions": row["max_submissions"], "starter_code": row["starter_code"], "test_code": row["test_code"], "credit": row["credit"], "data_files": row["data_files"].strip(), "show_expected": row["show_expected"], "show_test_code": row["show_test_code"], "show_answer": row["show_answer"], "show_student_submissions": row["show_student_submissions"], "expected_text_output": row["expected_text_output"].strip(), "expected_image_output": row["expected_image_output"], "date_created": row["date_created"], "date_updated": row["date_updated"]}

        if row["data_files"]:
            exercise_dict["data_files"] = json.loads(row["data_files"])

        if format_content:
            exercise_dict["expected_text_output"] = format_output_as_html(exercise_dict["expected_text_output"])
            exercise_dict["instructions"] = convert_markdown_to_html(exercise_dict["instructions"])
            exercise_dict["credit"] = convert_markdown_to_html(exercise_dict["credit"])
            exercise_dict["answer_description"] = convert_markdown_to_html(exercise_dict["answer_description"])
            exercise_dict["hint"] =  convert_markdown_to_html(exercise_dict["hint"])

        return exercise_dict

    def get_log_table_contents(self, file_path, year="No filter", month="No filter", day="No filter"):
        new_dict = {}
        line_num = 1
        with gzip.open(file_path) as read_file:
            header = read_file.readline()
            for line in read_file:
                line_items = line.decode().rstrip("\n").split("\t")

                #Get ids to create links to each course, assignment, and exercise in the table
                course_id = line_items[1]
                assignment_id = line_items[2]
                exercise_id = line_items[3]

                line_items[6] = f"<a href='/course/{course_id}'>{line_items[6]}</a>"
                line_items[7] = f"<a href='/assignment/{course_id}/{assignment_id}'>{line_items[7]}</a>"
                line_items[8] = f"<a href='/exercise/{course_id}/{assignment_id}/{exercise_id}'>{line_items[8]}</a>"

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
        root_dirs_to_log = set(["home", "course", "assignment", "exercise", "check_exercise", "edit_course", "edit_assignment", "edit_exercise", "delete_course", "delete_assignment", "delete_exercise", "view_answer", "import_course", "export_course"])
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

            self.execute(sql, [course_basics["title"], course_basics["visible"], course_details["introduction"], course_details["passcode"], course_details["date_updated"], course_basics["id"]])
        else:
            sql = '''INSERT INTO courses (title, visible, introduction, passcode, date_created, date_updated)
                     VALUES (?, ?, ?, ?, ?, ?)'''

            course_basics["id"] = self.execute(sql, [course_basics["title"], course_basics["visible"], course_details["introduction"], course_details["passcode"], course_details["date_created"], course_details["date_updated"]])
            course_basics["exists"] = True

        return course_basics["id"]

    def save_assignment(self, assignment_basics, assignment_details):
        if assignment_basics["exists"]:
            sql = '''UPDATE assignments
                     SET title = ?, visible = ?, introduction = ?, date_updated = ?, start_date = ?, due_date = ?, allow_late = ?, late_percent = ?, view_answer_late = ?, enable_help_requests = ?, has_timer = ?, hour_timer = ?, minute_timer = ?
                     WHERE course_id = ?
                       AND assignment_id = ?'''

            self.execute(sql, [assignment_basics["title"], assignment_basics["visible"], assignment_details["introduction"], assignment_details["date_updated"], assignment_details["start_date"], assignment_details["due_date"], assignment_details["allow_late"], assignment_details["late_percent"], assignment_details["view_answer_late"], assignment_details["enable_help_requests"], assignment_details["has_timer"], assignment_details["hour_timer"], assignment_details["minute_timer"], assignment_basics["course"]["id"], assignment_basics["id"]])
        else:
            sql = '''INSERT INTO assignments (course_id, title, visible, introduction, date_created, date_updated, start_date, due_date, allow_late, late_percent, view_answer_late, enable_help_requests, has_timer, hour_timer, minute_timer)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

            assignment_basics["id"] = self.execute(sql, [assignment_basics["course"]["id"], assignment_basics["title"], assignment_basics["visible"], assignment_details["introduction"], assignment_details["date_created"], assignment_details["date_updated"], assignment_details["start_date"], assignment_details["due_date"], assignment_details["allow_late"], assignment_details["late_percent"], assignment_details["view_answer_late"], assignment_details["enable_help_requests"], assignment_details["has_timer"], assignment_details["hour_timer"], assignment_details["minute_timer"]])

            assignment_basics["exists"] = True

        return assignment_basics["id"]

    def save_exercise(self, exercise_basics, exercise_details):
        if exercise_basics["exists"]:
            sql = '''UPDATE exercises
                     SET title = ?, visible = ?, answer_code = ?, answer_description = ?, hint = ?, max_submissions = ?,
                         credit = ?, data_files = ?, back_end = ?, expected_text_output = ?, expected_image_output = ?,
                         instructions = ?, output_type = ?, show_answer = ?, show_student_submissions = ?, show_expected = ?,
                         show_test_code = ?, starter_code = ?, test_code = ?, date_updated = ?
                     WHERE course_id = ?
                       AND assignment_id = ?
                       AND exercise_id = ?'''

            self.execute(sql, [exercise_basics["title"], exercise_basics["visible"], str(exercise_details["answer_code"]), exercise_details["answer_description"], exercise_details["hint"], exercise_details["max_submissions"], exercise_details["credit"], json.dumps(exercise_details["data_files"]), exercise_details["back_end"], exercise_details["expected_text_output"], exercise_details["expected_image_output"], exercise_details["instructions"], exercise_details["output_type"], exercise_details["show_answer"], exercise_details["show_student_submissions"], exercise_details["show_expected"], exercise_details["show_test_code"], exercise_details["starter_code"], exercise_details["test_code"], exercise_details["date_updated"], exercise_basics["assignment"]["course"]["id"], exercise_basics["assignment"]["id"], exercise_basics["id"]])
        else:
            sql = '''INSERT INTO exercises (course_id, assignment_id, title, visible, answer_code, answer_description, hint, max_submissions, credit, data_files, back_end, expected_text_output, expected_image_output, instructions, output_type, show_answer, show_student_submissions, show_expected, show_test_code, starter_code, test_code, date_created, date_updated)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

            exercise_basics["id"] = self.execute(sql, [exercise_basics["assignment"]["course"]["id"], exercise_basics["assignment"]["id"], exercise_basics["title"], exercise_basics["visible"], str(exercise_details["answer_code"]), exercise_details["answer_description"], exercise_details["hint"], exercise_details["max_submissions"], exercise_details["credit"], json.dumps(exercise_details["data_files"]), exercise_details["back_end"], exercise_details["expected_text_output"], exercise_details["expected_image_output"], exercise_details["instructions"], exercise_details["output_type"], exercise_details["show_answer"], exercise_details["show_student_submissions"], exercise_details["show_expected"], exercise_details["show_test_code"], exercise_details["starter_code"], exercise_details["test_code"], exercise_details["date_created"], exercise_details["date_updated"]])
            exercise_basics["exists"] = True

        return exercise_basics["id"]

    def save_submission(self, course, assignment, exercise, user, code, text_output, image_output, passed):
        submission_id = self.get_next_submission_id(course, assignment, exercise, user)
        sql = '''INSERT INTO submissions (course_id, assignment_id, exercise_id, user_id, submission_id, code, text_output, image_output, passed, date)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

        self.execute(sql, [int(course), int(assignment), int(exercise), user, int(submission_id), code, text_output, image_output, passed, datetime.now()])

        return submission_id

    def save_help_request(self, course, assignment, exercise, user_id, code, text_output, image_output, student_comment, date):
        sql = '''INSERT INTO help_requests (course_id, assignment_id, exercise_id, user_id, code, text_output, image_output, student_comment, approved, date, more_info_needed)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

        self.execute(sql, (course, assignment, exercise, user_id, code, text_output, image_output, student_comment, 0, date, 0,))

    def update_help_request(self, course, assignment, exercise, user_id, student_comment):
        sql = '''UPDATE help_requests
                 SET student_comment = ?, more_info_needed = ?, suggestion = ?, approved = ?
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND exercise_id = ?
                   AND user_id = ?'''
        self.execute(sql, (student_comment, 0, None, 0, course, assignment, exercise, user_id,))
    
    def delete_help_request(self, course, assignment, exercise, user_id):
        sql = '''DELETE FROM help_requests
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND exercise_id = ?
                   AND user_id = ?'''
        self.execute(sql, (course, assignment, exercise, user_id,))

    def save_help_request_suggestion(self, course, assignment, exercise, user_id, suggestion, approved, suggester_id, approver_id, more_info_needed):

        sql = '''UPDATE help_requests
                 SET suggestion = ?, approved = ?, suggester_id = ?, approver_id = ?, more_info_needed = ?
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND exercise_id = ?
                   AND user_id = ?'''

        self.execute(sql, (suggestion, approved, suggester_id, approver_id,  more_info_needed, course, assignment, exercise, user_id,))
    
    def copy_assignment(self, course_id, assignment_id, new_course_id):
        sql = '''INSERT INTO assignments (course_id, title, visible, introduction, date_created, date_updated, start_date, due_date, allow_late, late_percent, view_answer_late, enable_help_requests, has_timer, hour_timer, minute_timer)
                 SELECT ?, title, visible, introduction, date_created, date_updated, start_date, due_date, allow_late, late_percent, view_answer_late, enable_help_requests, has_timer, hour_timer, minute_timer
                 FROM assignments
                 WHERE course_id = ?
                   AND assignment_id = ?'''

        new_assignment_id = self.execute(sql, (new_course_id, course_id, assignment_id,))

        sql = '''INSERT INTO exercises (course_id, assignment_id, title, visible, answer_code, answer_description, hint, max_submissions, credit, data_files, back_end, expected_text_output, expected_image_output, instructions, output_type, show_answer, show_student_submissions, show_expected, show_test_code, starter_code, test_code, date_created, date_updated)
                 SELECT ?, ?, title, visible, answer_code, answer_description, hint, max_submissions, credit, data_files, back_end, expected_text_output, expected_image_output, instructions, output_type, show_answer, show_student_submissions, show_expected, show_test_code, starter_code, test_code, date_created, date_updated
                 FROM exercises
                 WHERE course_id = ?
                   AND assignment_id = ?'''

        self.execute(sql, (new_course_id, new_assignment_id, course_id, assignment_id,))

    def update_user(self, user_id, user_dict):
        self.set_user_dict_defaults(user_dict)

        sql = '''UPDATE users
                 SET name = ?, given_name = ?, family_name = ?, picture = ?, locale = ?
                 WHERE user_id = ?'''

        self.execute(sql, (user_dict["name"], user_dict["given_name"], user_dict["family_name"], user_dict["picture"], user_dict["locale"], user_id,))

    def update_user_settings(self, user_id, theme, use_auto_complete):
        sql = '''UPDATE users
                 SET ace_theme = ?, use_auto_complete = ?
                 WHERE user_id = ?'''
        self.execute(sql, (theme, use_auto_complete, user_id,))

    def remove_user_submissions(self, user_id):
        sql = '''SELECT submission_id
                 FROM submissions
                 WHERE user_id = ?'''

        submissions = self.fetchall(sql, (user_id,))
        if submissions:

            sql = '''DELETE FROM scores
                     WHERE user_id = ?'''
            self.execute(sql, (user_id,))

            sql = '''DELETE FROM submissions
                     WHERE user_id = ?'''
            self.execute(sql, (user_id,))

            return True
        else:
            return False

    def delete_user(self, user_id):
        sql = f'''DELETE FROM users
                  WHERE user_id = ?'''

        self.execute(sql, (user_id,))

    def move_exercise(self, course_id, assignment_id, exercise_id, new_assignment_id):
        self.execute(f'''UPDATE exercises
                         SET assignment_id = {new_assignment_id}
                         WHERE course_id = {course_id}
                           AND assignment_id = {assignment_id}
                           AND exercise_id = {exercise_id}''')

        self.execute(f'''UPDATE scores
                         SET assignment_id = {new_assignment_id}
                         WHERE course_id = {course_id}
                           AND assignment_id = {assignment_id}
                           AND exercise_id = {exercise_id}''')

        self.execute(f'''UPDATE submissions
                         SET assignment_id = {new_assignment_id}
                         WHERE course_id = {course_id}
                           AND assignment_id = {assignment_id}
                           AND exercise_id = {exercise_id}''')

    def delete_exercise(self, exercise_basics):
        c_id = exercise_basics["assignment"]["course"]["id"]
        a_id = exercise_basics["assignment"]["id"]
        e_id = exercise_basics["id"]

        self.execute(f'''DELETE FROM submissions
                         WHERE course_id = {c_id}
                           AND assignment_id = {a_id}
                           AND exercise_id = {e_id}''')

        self.execute(f'''DELETE FROM scores
                         WHERE course_id = {c_id}
                           AND assignment_id = {a_id}
                           AND exercise_id = {e_id}''')

        self.execute(f'''DELETE FROM exercises
                         WHERE course_id = {c_id}
                           AND assignment_id = {a_id}
                           AND exercise_id = {e_id}''')

    def delete_assignment(self, assignment_basics):
        c_id = assignment_basics["course"]["id"]
        a_id = assignment_basics["id"]

        self.execute(f'''DELETE FROM submissions
                         WHERE course_id = {c_id}
                           AND assignment_id = {a_id}''')

        self.execute(f'''DELETE FROM scores
                         WHERE course_id = {c_id}
                           AND assignment_id = {a_id}''')

        self.execute(f'''DELETE FROM exercises
                         WHERE course_id = {c_id}
                           AND assignment_id = {a_id}''')

        self.execute(f'''DELETE FROM assignments
                         WHERE course_id = {c_id}
                           AND assignment_id = {a_id}''')

    def delete_course(self, course_basics):
        c_id = course_basics["id"]

        self.execute(f'''DELETE FROM submissions
                         WHERE course_id = {c_id}''')

        self.execute(f'''DELETE FROM exercises
                         WHERE course_id = {c_id}''')

        self.execute(f'''DELETE FROM assignments
                         WHERE course_id = {c_id}''')

        self.execute(f'''DELETE FROM courses
                         WHERE course_id = {c_id}''')

        self.execute(f'''DELETE FROM permissions
                         WHERE course_id = {c_id}''')

    def delete_course_submissions(self, course_basics):
        c_id = course_basics["id"]

        self.execute(f'''DELETE FROM submissions
                        WHERE course_id = {c_id}''')

        self.execute(f'''DELETE FROM scores
                        WHERE course_id = {c_id}''')

    def delete_assignment_submissions(self, assignment_basics):
        c_id = assignment_basics["course"]["id"]
        a_id = assignment_basics["id"]

        self.execute(f'''DELETE FROM submissions
                         WHERE course_id = {c_id}
                           AND assignment_id = {a_id}''')

        self.execute(f'''DELETE FROM scores
                         WHERE course_id = {c_id}
                           AND assignment_id = {a_id}''')

    def delete_exercise_submissions(self, exercise_basics):
        c_id = exercise_basics["assignment"]["course"]["id"]
        a_id = exercise_basics["assignment"]["id"]
        e_id = exercise_basics["id"]

        self.execute(f'''DELETE FROM submissions
                         WHERE course_id = {c_id}
                           AND assignment_id = {a_id}
                           AND exercise_id = {e_id}''')

        self.execute(f'''DELETE FROM scores
                         WHERE course_id = {c_id}
                           AND assignment_id = {a_id}
                           AND exercise_id = {e_id}''')

    def create_scores_text(self, course_id, assignment_id):
        out_file_text = "Course_ID,Assignment_ID,Student_ID,Score\n"
        scores = self.get_assignment_scores(course_id, assignment_id)

        for student in scores:
            out_file_text += f"{course_id},{assignment_id},{student[0]},{student[1]['percent_passed']}\n"

        return out_file_text

    def export_data(self, course_basics, table_name, output_tsv_file_path):
        if table_name == "submissions":
            sql = '''SELECT c.title, a.title, e.title, s.user_id, s.submission_id, s.code, s.text_output, s.image_output, s.passed, s.date
                    FROM submissions s
                    INNER JOIN courses c
                      ON c.course_id = s.course_id
                    INNER JOIN assignments a
                      ON a.assignment_id = s.assignment_id
                    INNER JOIN exercises e
                      ON e.exercise_id = s.exercise_id
                    WHERE s.course_id = ?'''

        else:
            sql = f"SELECT * FROM {table_name} WHERE course_id = ?"

        rows = []
        for row in self.fetchall(sql, (course_basics["id"],)):
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

    def rebuild_exercises(self, assignment_title):
        sql = '''SELECT e.*
                 FROM exercises e
                 INNER JOIN assignments a
                   ON e.course_id = a.course_id AND e.assignment_id = a.assignment_id
                 WHERE a.title = ?'''

        for row in self.fetchall(sql, (assignment_title, )):
            course = row["course_id"]
            assignment = row["assignment_id"]
            exercise = row["exercise_id"]
            print(f"Rebuilding course {course}, assignment {assignment}, exercise {exercise}")

            exercise_basics = self.get_exercise_basics(course, assignment, exercise)
            exercise_details = self.get_exercise_details(course, assignment, exercise)

            text_output, image_output = exec_code(self.__settings_dict, exercise_details["answer_code"], exercise_basics, exercise_details)

            exercise_details["expected_text_output"] = text_output
            exercise_details["expected_image_output"] = image_output
            self.save_exercise(exercise_basics, exercise_details)

    def rerun_submissions(self, assignment_title):
        sql = '''SELECT course_id, assignment_id
                 FROM assignments
                 WHERE title = ?'''

        row = self.fetchone(sql, (assignment_title, ))
        course = int(row["course_id"])
        assignment = int(row["assignment_id"])

        sql = '''SELECT *
                 FROM submissions
                 WHERE course_id = ? AND assignment_id = ? AND passed = 0
                 ORDER BY exercise_id, user_id, submission_id'''

        for row in self.fetchall(sql, (course, assignment, )):
            exercise = row["exercise_id"]
            user = row["user_id"]
            submission = row["submission_id"]
            code = row["code"].replace("\r", "")
            print(f"Rerunning submission {submission} for course {course}, assignment {assignment}, exercise {exercise}, user {user}.")

            exercise_basics = self.get_exercise_basics(course, assignment, exercise)
            exercise_details = self.get_exercise_details(course, assignment, exercise)

            text_output, image_output = exec_code(self.__settings_dict, code, exercise_basics, exercise_details, None)
            diff, passed = check_exercise_output(exercise_details["expected_text_output"], text_output, exercise_details["expected_image_output"], image_output, exercise_details["output_type"])

            sql = '''UPDATE submissions
                     SET text_output = ?,
                         image_output = ?,
                         passed = ?
                     WHERE course_id = ?
                       AND assignment_id = ?
                       AND exercise_id = ?
                       AND user_id = ?
                       AND submission_id = ?'''

            self.execute(sql, [text_output, image_output, passed, int(course), int(assignment), int(exercise), user, int(submission)])
