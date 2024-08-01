# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

import atexit
import sqlite3
import traceback
#################
import sys
sys.path.append('/app')
from helper import *

settings_dict = load_yaml_dict(read_file("../Settings.yaml"))

conn = sqlite3.connect("/database/CodeBuddy.db", isolation_level=None, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys=ON")

atexit.register(conn.close)
atexit.register(cursor.close)

version = read_file("../VERSION").rstrip()

# This tells us whether the migration has already happened.
check_sql = '''SELECT COUNT(*) AS count
               FROM pragma_table_info("courses")
               WHERE name = "passcode"'''

cursor.execute(check_sql)
check_result = cursor.fetchone()["count"]

if check_result > 0:
    print("***NotNeeded***")
else:
    with open("/migration_scripts/3_to_4.sql") as sql_file:
        sql_statements = sql_file.read().split(";")

    try:
        for sql in sql_statements:
            print(sql)
            cursor.executescript(sql)
        print("***Success***")
    except:
        print(traceback.format_exc())
