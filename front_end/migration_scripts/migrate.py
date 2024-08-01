# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

import atexit
import sqlite3
import sys
import traceback

sys.path.append('./server')
from content import *
from helper import *

# Example value: 8_to_9
migration_numbers = sys.argv[1]
version = int(sys.argv[2])

# There must be two SQL files for each migration. One checks
# whether the migration has already occurred. The other modifies the
# database. Using the example value, these files would be called
# 8_to_9_check.sql and 8_to_9_migrate.sql, respectively.
# The check query must have a column called "count" in the select
# statement.
check_file_path = f"migration_scripts/{migration_numbers}_check.sql"
migrate_file_path = f"migration_scripts/{migration_numbers}_migrate.sql"

content = Content()

check_sql = read_file(check_file_path)

if content.fetchone(check_sql)["count"] > 0:
    print("***NotNeeded***")
else:
    sql_statements = read_file(migrate_file_path).split(";")
    params_list = [() for x in sql_statements]

    try:
        content.execute_multiple(sql_statements, params_list)

        if version >= 39:
            content.update_all_when_content_updated()
    
        print("***Success***")
    except:
        print(traceback.format_exc())