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
            help_request = {"user_id": request["user_id"], "name": request["name"], "code": request["code"], "text_output": request["text_output"], "image_output": request["text_output"], "image_output": request["image_output"], "student_comment": request["student_comment"], "approved": request["approved"], "suggester_id": request["suggester_id"], "approver_id": request["approver_id"], "more_info_needed": request["more_info_needed"]}
            if request["suggestion"]:
                help_request["suggestion"] = request["suggestion"]
            else:
                help_request["suggestion"] = None

            return help_request

    def compare_help_requests(self, course_id, assignment_id, exercise_id, user_id):
        sql = '''SELECT r.text_output, e.expected_text_output, r.image_output, e.expected_image_output
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

        orig_output = None

        if row["image_output"]:
            if row["image_output"] != row["expected_image_output"]:
                orig_output = row["image_output"]

        else:
            if row["text_output"] != row["expected_text_output"]:
                orig_output = re.sub("#.*", "", row["text_output"])
                #print(orig_output)

        if orig_output:
                sql = '''SELECT r.course_id, r.assignment_id, r.exercise_id, r.user_id, u.name, r.code, r.text_output, r.image_output, r.student_comment, r.suggestion
                        FROM help_requests r
                        INNER JOIN users u
                        ON r.user_id = u.user_id
                        WHERE r.course_id = ?
                        AND NOT r.user_id = ?'''
                requests = self.fetchall(sql, (course_id, user_id,))
                sim_dict = []

                if row["image_output"]:
                    for request in requests:
                        diff_image, diff_percent = diff_jpg(orig_output, request["image_output"])
                        if diff_percent < .10:
                            request_info = {"psim": 100 - diff_percent, "course_id": request["course_id"], "assignment_id": request["assignment_id"], "exercise_id": request["exercise_id"], "user_id": request["user_id"], "name": request["name"], "student_comment": request["student_comment"],  "code": request["code"], "text_output": request["text_output"], "suggestion": request["suggestion"]}
                            sim_dict.append(request_info)

                else:

                    nlp = spacy.load('en_core_web_sm')
                    orig = nlp(orig_output)

                    for request in requests:
                        #print(request["text_output"])
                        curr = nlp(re.sub("#.*", "", request["text_output"]))
                        psim = curr.similarity(orig)
                        #print(psim)
                        if psim >= .90:
                            request_info = {"psim": psim, "course_id": request["course_id"], "assignment_id": request["assignment_id"], "exercise_id": request["exercise_id"], "user_id": request["user_id"], "name": request["name"], "student_comment": request["student_comment"],  "code": request["code"], "text_output": request["text_output"], "suggestion": request["suggestion"]}
                            sim_dict.append(request_info)
                            
                    #self.test_similarity()
                    return sim_dict

    def test_similarity(self):
        nlp = spacy.load('en_core_web_sm')
        orig = nlp("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")
        curr = nlp("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")
        diff_image, diff_percent = diff_jpg(orig, curr)
        print(diff_percent)
        
        psim = curr.similarity(orig)
        print(psim)
        if len(orig) < 10 and len(curr) < 10:
            if psim > .30:
                print("yes")
        elif len(orig) < 100 and len(curr) < 100:
            if psim > .50:
                print("yes")
        elif len(orig) < 200 and len(curr) < 200:
            if psim > .70:
                print("yes")
        else:
            if psim > .90:
                print("yes")

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
