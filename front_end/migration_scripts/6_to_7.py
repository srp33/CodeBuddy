# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

import atexit
import sqlite3
import traceback
#################
import sys
sys.path.append('./server')
from helper import *

settings_dict = load_yaml_dict(read_file("../Settings.yaml"))

conn = open_db("CodeBuddy.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys=OFF")

atexit.register(conn.close)
atexit.register(cursor.close)

version = read_file("../VERSION").rstrip()

# This tells us whether the migration has already happened.
check_sql = '''SELECT COUNT(*) AS count
               FROM pragma_table_info("problems")
               WHERE name = "data_files"'''

cursor.execute(check_sql)
check_result = cursor.fetchone()["count"]

if check_result > 0:
    print("***NotNeeded***")
else:
    with open("migration_scripts/6_to_7.sql") as sql_file:
        sql_statements = sql_file.read().split(";")

    try:
        for sql in sql_statements:
            print(sql)
            cursor.executescript(sql)

        credit_exists = '''SELECT credit, problem_id
                           FROM problems'''

        cursor.execute(credit_exists)
        for row in cursor.fetchall():
            if row["credit"] != "":
                insert_old_data_sql = '''UPDATE problems2
                                         SET credit = (SELECT credit || ' The data originated from [here](' || data_url || ').'
                                                       FROM problems
                                                       WHERE problem_id = ?)
                                         WHERE problem_id = ?'''

                cursor.execute(insert_old_data_sql, (row["problem_id"], row["problem_id"], ))

        data_sql = '''SELECT data_file_name, data_contents, problem_id
                      FROM problems'''

        cursor.execute(data_sql)
        for row in cursor.fetchall():
            if row["data_file_name"] != "":
                data_dict = {row["data_file_name"]: row["data_contents"]}
                data_string = json.dumps(data_dict)
            else:
                data_string = ""

            insert_data_sql = '''UPDATE problems2
                                 SET data_files = ?
                                 WHERE problem_id = ?'''

            cursor.execute(insert_data_sql, (data_string, row["problem_id"],))

        drop_table_sql = '''DROP TABLE IF EXISTS problems'''
        cursor.execute(drop_table_sql)

        rename_table_sql = '''ALTER TABLE problems2 RENAME TO problems'''
        cursor.execute(rename_table_sql)

        print("***Success***")
    except:
        print(traceback.format_exc())
