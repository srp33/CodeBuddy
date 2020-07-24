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
import html

def get_environments():
    return load_yaml_dict(read_file("/Environments.yaml"))

class Content:
    __DB_LOCATION = r"/submissions/test.db"
    #__DB_LOCATION = get_environments()["db_location"]

    def __init__(self):
        self.conn = sqlite3.connect(self.__DB_LOCATION)
        self.c = self.conn.cursor()

        self.c.execute("PRAGMA foreign_keys=ON")

        # if not self.check_user_exists():
        #     self.create_user()
        # else:
        #     self.get_user()

        atexit.register(self.close)

    def close(self):
        self.c.close()
        self.conn.close()

    def create_table(self, create_table_sql):
        try:
            self.c.execute(create_table_sql)
        except Error as e:
            print(e)

    def create_sqlite_tables(self): #make id's integers?
        create_users_table = """ CREATE TABLE IF NOT EXISTS users (
                                            user_id text PRIMARY KEY
                                        ); """

        create_permissions_table = """ CREATE TABLE IF NOT EXISTS permissions (
                                            user_id	text NOT NULL, 
                                            role text NOT NULL,
                                            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                                            PRIMARY KEY (user_id)
                                        ); """        

        create_courses_table = """ CREATE TABLE IF NOT EXISTS courses (
                                        course_id text NOT NULL,
                                        title text NOT NULL UNIQUE,
                                        visible integer NOT NULL,
                                        introduction text,
                                        PRIMARY KEY (course_id)
                                    ); """

        create_assignments_table = """ CREATE TABLE IF NOT EXISTS assignments (
                                            course_id text NOT NULL,
                                            assignment_id text NOT NULL,
                                            title text NOT NULL UNIQUE,
                                            visible integer NOT NULL,
                                            introduction text,
                                            FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE,
                                            PRIMARY KEY (assignment_id)
                                        ); """

        # create_assignments_course_index = """ CREATE UNIQUE INDEX IF NOT EXISTS idx_course_id ON assignments (course_id) """ # Not sure how indexes work with foreign keys, we might not need this one

        create_problems_table = """ CREATE TABLE IF NOT EXISTS problems (
                                        course_id text NOT NULL,
                                        assignment_id text NOT NULL,
                                        problem_id text NOT NULL,
                                        title text NOT NULL UNIQUE,
                                        visible integer NOT NULL,
                                        answer_code text NOT NULL,
                                        answer_description text,
                                        credit text,
                                        data_url text,
                                        environment text NOT NULL,
                                        expected_output text NOT NULL,
                                        instructions text NOT NULL,
                                        output_type text NOT NULL,
                                        show_answer integer NOT NULL,
                                        show_expected integer NOT NULL,
                                        show_test_code integer NOT NULL,
                                        test_code text,
                                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE,
                                        FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE,
                                        PRIMARY KEY (problem_id)
                                    ); """

        # create_problems_assignment_index = """ CREATE UNIQUE INDEX IF NOT EXISTS idx_assignment_id ON problems (assignment_id) """ # Not sure how indexes work with foreign keys, we might not need this one

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
                                            FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE,
                                            FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE,
                                            FOREIGN KEY (problem_id) REFERENCES problems (problem_id) ON DELETE CASCADE,
                                            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                                            PRIMARY KEY (course_id, assignment_id, problem_id, user_id, submission_id)
                                        ); """

        # create_submissions_course_index = """ CREATE UNIQUE INDEX IF NOT EXISTS idx_course_id ON submissions (course_id) """
        # create_submissions_assignment_index = """ CREATE UNIQUE INDEX IF NOT EXISTS idx_assignment_id ON submissions (assignment_id) """
        # create_submissions_problem_index = """ CREATE UNIQUE INDEX IF NOT EXISTS idx_problem_id ON submissions (problem_id) """ 

        if self.conn is not None:            
            self.create_table(create_users_table)
            self.create_table(create_permissions_table)
            self.create_table(create_courses_table)
            self.create_table(create_assignments_table)
            self.create_table(create_problems_table)
            self.create_table(create_submissions_table)

            print("Here are all the submissions:")
            self.print_rows("submissions")
            print("Here are all the problems:")
            self.print_rows("problems")

            # self.c.execute(create_courses_index)
            # self.c.execute(create_assignments_course_index)
            # self.c.execute(create_assignments_index)
            # self.c.execute(create_problems_assignment_index)
            # self.c.execute(create_problems_index)
            # self.c.execute(create_submissions_course_index)
            # self.c.execute(create_submissions_assignment_index)
            # self.c.execute(create_submissions_problem_index)
            # self.c.execute(create_submissions_index)

        else:
            print("Error! Cannot create the database connection.")

    # #### Access to certain pages depends on the user's role. If the user is in the users table, look up their role in the permissions table. If the user is not in the permissions table, look up role in permissions yaml file, then add to permissions and users tables. ####

    # def check_user_exists(self, user_id): #checks if user exists. If not, they are found in the permissions table and added to the users table
    #     sql = 'SELECT user_id FROM users WHERE user_id = ?'

    #     self.c.execute(sql, (user_id,))
    #     exists = self.c.fetchone()

    #     if exists is None:
    #         return False
    #     else:
    #         return True

    # def get_role(self, user_id): #looks up role of given user_id in permissions yaml file. If not there, added as student to permissions table
    #     sql = 'SELECT user_id FROM permissions WHERE user_id = ?'

    #     self.c.execute(sql, (user_id,))
    #     row = self.c.fetchone()
    #     return row[1]

    # def add_user(self, user_id):

    # def add_role(self, user_id):

    def print_tables(self):
        tables = self.c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for table in tables:
            print(table[0])

    def print_rows(self, table):
        self.c.execute(''' SELECT * FROM ''' + table)
        rows = self.c.fetchall()    #fetchall is not good for memory if there is a large number of entries in table
        for row in rows:
            print(row)
        # rows = self.c.execute('SELECT * FROM ' + table)
        # for row in rows:
        #     print(row[0])

    def check_course_exists(self, course):
        sql = 'SELECT * FROM courses WHERE course_id=?'
        self.c.execute(sql, (course,))
        return self.c.fetchone()

    def check_assignment_exists(self, assignment):
        sql = 'SELECT * FROM assignments WHERE assignment_id=?'
        self.c.execute(sql, (assignment,))
        return self.c.fetchone()

    def check_problem_exists(self, problem):
        sql = 'SELECT * FROM problems WHERE problem_id=?'
        self.c.execute(sql, (problem,))
        return self.c.fetchone()

    def get_courses(self, show_hidden=True):
        courses = []
        sql = 'SELECT course_id FROM courses'
        #self.conn.row_factory = lambda cursor, row: row[0]  #converts tuples to plain list--does this do anything??
        #course_ids = self.c.execute(sql).fetchall()
        course_ids = self.c.execute(sql)
        course_ids = [ x[0] for x in self.c.fetchall()]     #converts tuples to list
        print("Here are all the course ids from course table:")
        print(course_ids)

        for course_id in course_ids:
            course_basics = self.get_course_basics(course_id)
            if course_basics["visible"] or show_hidden:
                courses.append([course_id, course_basics])

        return self.sort_nested_list(courses)

    def get_assignments(self, course_id, show_hidden=True):
        sql = 'SELECT assignment_id FROM assignments WHERE course_id=?'
        assignments = []
        self.conn.row_factory = lambda cursor, row: row[0]
        #assignment_ids = self.c.execute(sql).fetchall()
        assignment_ids = self.c.execute(sql, (str(course_id),))
        assignment_ids = [ x[0] for x in self.c.fetchall()]     #converts tuples to list
        print("Here are all the assignment ids from assignment table:")
        print(assignment_ids)

        for assignment_id in assignment_ids:
            assignment_basics = self.get_assignment_basics(course_id, assignment_id)
            if assignment_basics["visible"] or show_hidden:
                assignments.append([assignment_id, assignment_basics])

        return self.sort_nested_list(assignments)

    def get_problems(self, course_id, assignment_id, show_hidden=True):
        sql = 'SELECT problem_id FROM problems WHERE assignment_id=?'
        problems = []
        self.conn.row_factory = lambda cursor, row: row[0]
        #problem_ids = self.c.execute(sql).fetchall()
        problem_ids = self.c.execute(sql, (str(assignment_id),))
        problem_ids = [ x[0] for x in self.c.fetchall()]     #converts tuples to list
        #print("Here are all the problem ids from problem table:")
        #print(problem_ids)

        for problem_id in problem_ids:
            problem_basics = self.get_problem_basics(course_id, assignment_id, problem_id)
            if problem_basics["visible"] or show_hidden:
                problems.append([problem_id, problem_basics])

        return self.sort_nested_list(problems)

    def get_submissions_basic(self, course_id, assignment_id, problem_id, user):
        sql_ids = 'SELECT submission_id FROM submissions WHERE problem_id=?'
        submissions = []
        self.conn.row_factory = lambda cursor, row: row[0]
        submission_ids = self.c.execute(sql_ids, (str(problem_id),))
        submission_ids = [x[0] for x in self.c.fetchall()]     #converts tuples to list
        print("Here are all the submission ids from submission table:")
        print(submission_ids)

        if(len(submission_ids) > 0):
            for submission_id in submission_ids:
                self.conn.row_factory = sqlite3.Row
                sql_basics = 'SELECT date, passed FROM submissions WHERE submission_id=?'
                self.c.execute(sql_basics, (str(submission_id),))
                row = self.c.fetchone()
                submission_dict = {"date": row[0], "passed": row[1]}
                submissions.append([submission_id, submission_dict["date"], submission_dict["passed"]])
            print("here are the submissions' basic info:")
            print(submissions)
            return sorted(submissions, key = lambda x: x[0], reverse=True)

        return submissions

    def get_course_basics(self, course_id):
        if not course_id:
            course_id = create_id(self.get_courses())

        course_dict = {"id": course_id, "title": "", "visible": True, "exists": False}

        self.conn.row_factory = sqlite3.Row #supposed to let us access values by column name, but not working, might need to move it to when initialize conn
        sql = 'SELECT course_id, title, visible FROM courses WHERE course_id = ?'

        self.c.execute(sql, (str(course_id),))
        row = self.c.fetchone()
        if row is None:
            return course_dict
        else:
            course_dict = {"id": row[0], "title": row[1], "visible": row[2], "exists": True}

        return course_dict

    def get_assignment_basics(self, course_id, assignment_id):
        if not assignment_id:
            assignment_id = create_id(self.get_assignments(course_id))

        course_basics = self.get_course_basics(course_id)
        assignment_dict = {"id": assignment_id, "title": "", "visible": True, "exists": False, "course": course_basics}

        self.conn.row_factory = sqlite3.Row
        sql = 'SELECT assignment_id, title, visible FROM assignments WHERE assignment_id = ?'
        self.c.execute(sql, (str(assignment_id),))
        row = self.c.fetchone()
        if row is None:
            return assignment_dict
        else:
            assignment_dict = {"id": row[0], "title": row[1], "visible": row[2], "exists": True}

        return assignment_dict

    def get_problem_basics(self, course_id, assignment_id, problem_id): #since we're not saving file paths, do we need to save id's in dictionaries too?
        if not problem_id:
            problem_id = create_id(self.get_problems(course_id, assignment_id))

        assignment_basics = self.get_assignment_basics(course_id, assignment_id)
        problem_dict = {"id": problem_id, "title": "", "visible": True, "exists": False, "assignment": assignment_basics}

        self.conn.row_factory = sqlite3.Row
        sql = 'SELECT problem_id, title, visible FROM problems WHERE problem_id = ?'
        self.c.execute(sql, (str(problem_id),))
        row = self.c.fetchone()
        if row is None:
            return problem_dict
        else:
            problem_dict = {"id": row[0], "title": row[1], "visible": row[2], "exists": True}

        return problem_dict

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
        sql = 'SELECT COUNT(*) FROM submissions'
        num_submissions = self.c.execute(sql).fetchone()[0]
        print("Here is the number of submissions for this problem:")
        print(num_submissions)
        return num_submissions

    def get_next_submission_id(self, course, assignment, problem, user):
        return self.get_num_submissions(course, assignment, problem, user) + 1

    def get_last_submission(self, course, assignment, problem, user):
        last_submission_id = self.get_num_submissions(course, assignment, problem, user)

        self.conn.row_factory = sqlite3.Row
        sql = 'SELECT code, code_output, passed, date, error_occurred FROM submissions WHERE submission_id = ?'
        self.c.execute(sql, (str(last_submission_id),))
        row = self.c.fetchone()
        
        code_output = html.unescape(row[1]).strip()
        
        last_submission = {"id": last_submission_id, "code": row[0], "code_output": code_output, "passed": row[2], "date": row[3], "error_occurred": row[4], "exists": True}

        return last_submission

    def get_submission_info(self, course, assignment, problem, user, submission_id): #with database we don't need to pass in anything besides submission_id
        self.conn.row_factory = sqlite3.Row
        sql = 'SELECT code, code_output, passed, date, error_occurred FROM submissions WHERE submission_id = ?'
        self.c.execute(sql, (submission_id,))
        row = self.c.fetchone()
        print("before: ", row[1])
        code_output = html.unescape(row[1]).strip()
        print("after: ", code_output)
        submission_dict = {"id": submission_id, "code": row[0], "code_output": code_output, "passed": row[2], "date": row[3], "error_occurred": row[4], "exists": True}

        return submission_dict

    def get_course_details(self, course, format_output=False):
        course_dict = {"introduction": ""}

        self.conn.row_factory = sqlite3.Row
        sql = 'SELECT introduction FROM courses WHERE course_id = ?'
        self.c.execute(sql, (course,))
        row = self.c.fetchone()
        if row is None:
            return course_dict
        else:
            course_dict = {"introduction": row[0]}
            if format_output:
                course_dict["introduction"] = convert_markdown_to_html(course_dict["introduction"])

        return course_dict

    def get_assignment_details(self, course, assignment, format_output=False):
        assignment_dict = {"introduction": ""}

        self.conn.row_factory = sqlite3.Row
        sql = 'SELECT introduction FROM assignments WHERE assignment_id = ?'
        self.c.execute(sql, (assignment,))
        row = self.c.fetchone()
        if row is None:
            return assignment_dict
        else:
            assignment_dict = {"introduction": row[0]}
            if format_output:
                assignment_dict["introduction"] = convert_markdown_to_html(assignment_dict["introduction"])

        return assignment_dict

    def get_problem_details(self, course, assignment, problem, format_content=False): #, parse_data_urls=False):
        problem_dict = {}
        self.conn.row_factory = sqlite3.Row
        sql = '''SELECT instructions, environment, output_type, answer_code, answer_description, test_code, credit, show_expected, show_test_code, show_answer, expected_output, data_url 
                    FROM problems WHERE problem_id = ?'''
        self.c.execute(sql, (problem,))
        row = self.c.fetchone()
        if row is None:
            problem_dict = {"instructions": "", "environment": "r_back_end",
                "output_type": "txt", "answer_code": "", "answer_description": "", "test_code": "",
                "credit": "", "show_expected": True, "show_test_code": True, "show_answer": True,
                "expected_output": "", "data_url": ""}
        else:
            problem_dict = {"instructions": row[0], "environment": row[1], "output_type": row[2], "answer_code": row[3], "answer_description": row[4], "test_code": row[5], "credit": row[6], "show_expected": row[7], "show_test_code": row[8], "show_answer": row[9], "expected_output": row[10], "data_url": row[11]}

            if format_content:
                problem_dict["instructions"] = convert_markdown_to_html(problem_dict["instructions"])
                problem_dict["credit"] = convert_markdown_to_html(problem_dict["credit"])

                if "answer_description" not in problem_dict:
                    problem_dict["answer_description"] = ""
                else:
                    problem_dict["answer_description"] = convert_markdown_to_html(problem_dict["answer_description"])

            #if parse_data_urls:
            #    problem_dict["data_urls"] = "\n".join([x[0] for x in problem_dict["data_urls_info"]])

            # This was added later, so adding it for backward compatibility
            if "answer_description" not in problem_dict:
                problem_dict["answer_description"] = ""
            if "show_answer" not in problem_dict:
                problem_dict["show_answer"] = ""

        return problem_dict

    def sort_nested_list(self, nested_list, key="title"):
        l_dict = {}
        for row in nested_list:
            l_dict[row[1][key]] = row

        sorted_list = []
        for key in sort_nicely(l_dict):
            sorted_list.append(l_dict[key])

        return sorted_list

    def has_duplicate_title(self, entries, this_entry, proposed_title): #might not need this since we're saving title as unique index
        print(entries)
        for entry in entries:
            print(entry)
            if entry[0] != this_entry and entry[1]["title"] == proposed_title:
                return True
        return False
    
    def add_row_users(self, user_id):
        sql = ''' INSERT INTO users (user_id) VALUES (?)'''
        self.c.execute(sql, [user_id])
        self.conn.commit()

    def add_row_permissions(self, user_id, role):
        sql = ''' INSERT INTO 
                    permissions (user_id, role) 
                    VALUES (?, ?)'''
        self.c.execute(sql, [user_id, role])
        self.conn.commit()

    def save_course(self, course_basics, course_details):
        sql = ''' INSERT INTO 
            courses (course_id, title, visible, introduction) 
            VALUES (?, ?, ?, ?)'''
        self.c.execute(sql, [course_basics["id"], course_basics["title"], course_basics["visible"], course_details["introduction"]])
        self.conn.commit()
        print("Here are all the courses:")
        self.print_rows("courses")

    def save_assignment(self, course, assignment_basics, assignment_details):
        sql = ''' INSERT INTO 
                    assignments (course_id, assignment_id, title, visible, introduction) 
                    VALUES (?, ?, ?, ?, ?)'''
        self.c.execute(sql, [course, assignment_basics["id"], assignment_basics["title"], assignment_basics["visible"], assignment_details["introduction"]])
        self.conn.commit()
        print("Here are all the assignments:")
        self.print_rows("assignments")

    def save_problem(self, course, assignment, problem_basics, problem_details):
        #if "data_urls" in problem_details:
        #    del problem_details["data_urls"]

        sql = ''' INSERT INTO 
                    problems (course_id, assignment_id, problem_id, title, visible, answer_code, answer_description, credit, data_url, environment, expected_output, instructions, output_type, show_answer, show_expected, show_test_code, test_code) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        self.c.execute(sql, [course, assignment, problem_basics["id"], problem_basics["title"], problem_basics["visible"], problem_details["answer_code"], problem_details["answer_description"], problem_details["credit"], problem_details["data_url"], problem_details["environment"], problem_details["expected_output"], problem_details["instructions"], problem_details["output_type"], problem_details["show_answer"], problem_details["show_expected"], problem_details["show_test_code"], problem_details["test_code"]])
        self.conn.commit()
        print("Here are all the problems:")
        self.print_rows("problems")

    def save_submission(self, course, assignment, problem, user, code, code_output, passed, date, error_occurred):
        submission_id = self.get_next_submission_id(course, assignment, problem, user)
        sql = ''' INSERT INTO 
                    submissions (course_id, assignment_id, problem_id, user_id, submission_id, code, code_output, passed, date, error_occurred) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        self.c.execute(sql, [course, assignment, problem, user, submission_id, code, code_output, passed, date, error_occurred])
        self.conn.commit()
        print("Here are all the submissions:")
        self.print_rows("submissions")
        return submission_id

    def update_user(self, old_id, new_id):
        sql = 'UPDATE users SET user_id = ? WHERE user_id'
        self.c.execute(sql, (new_id, old_id,))

    def update_permissions(self, user_id, new_permission):
        sql = 'UPDATE users SET permission = ? WHERE user_id = ?'
        self.c.execute(sql, (new_permission, user_id,))

    def update_course(self, course_id, col_name, new_value):
        sql = 'UPDATE courses SET ' + col_name + '=? WHERE course_id=?'
        self.c.execute(sql, (new_value, course_id,))
        self.conn.commit()

    def update_assignment(self, assignment_id, col_name, new_value):
        sql = 'UPDATE assignments SET ' + col_name + '=? WHERE assignment_id=?'
        self.c.execute(sql, (new_value, assignment_id,))
        self.conn.commit()

    def update_problem(self, problem_id, col_name, new_value):
        sql = 'UPDATE problems SET ' + col_name + '=? WHERE problem_id=?'
        self.c.execute(sql, (new_value, problem_id,))
        self.conn.commit()

    def delete_rows_with_value(self, table, col_name, value):
        sql = 'DELETE FROM ' + table + ' WHERE ' + col_name + '=?'
        self.c.execute(sql, (value,))
        self.conn.commit()

    def delete_all_rows(self, table):
        sql = 'DELETE FROM ' + table
        self.c.execute(sql)
        self.conn.commit()

    def delete_table(self, table):
        sql = 'DROP TABLE ' + table
        self.c.execute(sql)
        self.conn.commit()

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