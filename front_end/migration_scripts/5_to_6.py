import atexit
import sqlite3
import traceback
#################
import sys, os

sys.path.append('./server')
from helper import *

settings_dict = load_yaml_dict(read_file("../Settings.yaml"))

conn = open_db("CodeBuddy.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys=ON")

atexit.register(conn.close)
atexit.register(cursor.close)

version = read_file("../VERSION").rstrip()

# This tells us whether the migration has already happened.
check_sql = '''SELECT COUNT(*) AS count
               FROM pragma_table_info("users")
               WHERE name = "use_auto_complete"'''

cursor.execute(check_sql)
check_result = cursor.fetchone()["count"]

if check_result > 0:
    print("***NotNeeded***")
else:
    with open("migration_scripts/5_to_6.sql") as sql_file:
        sql_statements = sql_file.read().split(";")

    try:
        for sql in sql_statements:
            print(sql)
            cursor.executescript(sql)
        print("***Success***")
    except:
        print(traceback.format_exc())
