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
        help_requests = []

        sql = '''SELECT r.course_id, r.assignment_id, r.exercise_id, r.user_id, u.name, r.code, r.text_output, r.image_output, r.student_comment, r.suggestion, r.approved, r.suggester_id, r.approver_id, r.more_info_needed
                 FROM help_requests r
                 INNER JOIN users u
                   ON r.user_id = u.user_id
                 WHERE r.course_id = ?
                   AND r.assignment_id = ?
                   AND r.exercise_id = ?
                   AND NOT r.user_id = ?
                 ORDER BY r.date DESC'''

        for request in self.fetchall(sql, (course_id, assignment_id, exercise_id, user_id,)):
            help_requests.append({"course_id": request["course_id"], "assignment_id": request["assignment_id"], "exercise_id": request["exercise_id"], "user_id": request["user_id"], "name": request["name"], "code": request["code"], "text_output": request["text_output"], "image_output": request["text_output"], "image_output": request["image_output"], "student_comment": request["student_comment"], "suggestion": request["suggestion"], "approved": request["approved"], "suggester_id": request["suggester_id"], "approver_id": request["approver_id"], "more_info_needed": request["more_info_needed"]})

        return help_requests

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
        sql = '''SELECT code
                 FROM help_requests
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND exercise_id = ?
                   AND user_id = ?'''
        row = self.fetchone(sql, (course_id, assignment_id, exercise_id, user_id,))
        orig_code = re.sub("#.*", "", row["code"])

        sql = '''SELECT r.user_id, u.name, r.code, r.student_comment, r.suggestion
                 FROM help_requests r
                 INNER JOIN users u
                   ON r.user_id = u.user_id
                 WHERE r.course_id = ?
                   AND r.assignment_id = ?
                   AND r.exercise_id = ?
                   AND NOT r.user_id = ?'''
        requests = self.fetchall(sql, (course_id, assignment_id, exercise_id, user_id,))

        nlp = spacy.load('en_core_web_sm')
        orig = nlp(orig_code)
        sim_dict = []

        for request in requests:
            curr = nlp(re.sub("#.*", "", request["code"]))
            psim = curr.similarity(orig)
            print(psim)
            if psim >= .70:
                request_info = {"user_id": request["user_id"], "name": request["name"], "code": request["code"], "student_comment": request["student_comment"], "suggestion": request["suggestion"]}
                sim_dict.append(request_info)
                
        return sim_dict

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
