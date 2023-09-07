# <copyright_statement>
#   CodeBuddy - A learning management system for computer programming
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

import atexit
import sqlite3
import sys
import os
import traceback

sys.path.append('./server')
from helper import *
from content import *

content = Content()

version = read_file("../VERSION").rstrip()

# This tells us whether the migration has already happened.
check_sql = '''SELECT COUNT(*) AS count
               FROM pragma_table_info("tests")
               WHERE name = "code"'''

if content.fetchone(check_sql)["count"] > 0:
    print("***NotNeeded***")
else:
    with open("migration_scripts/15_to_16.sql") as sql_file:
        sql_statements = sql_file.read().split(";")

    if os.path.isfile("logs/progress.log"):
        print("ABC")
        try:
            with open("logs/progress.log", "a") as progress_file:
                for sql in sql_statements:
                    progress_file.write(sql + "\n")
                    content.execute(sql)

            print("***Success***")
        except:
            print(traceback.format_exc())

            try:
                with open("logs/progress.log", "a") as progress_file:
                    progress_file.write(traceback.format_exc())
            except:
                pass
    else:
        for sql in sql_statements:
            content.execute(sql)
        print("***Success***")
