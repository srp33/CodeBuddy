import atexit
import sqlite3
import traceback
#################
import sys
sys.path.append('/app')
from helper import *
from content import *

settings_dict = load_yaml_dict(read_file("/Settings.yaml"))
content = Content(settings_dict)


conn = sqlite3.connect(f"/database/{settings_dict['db_name']}", isolation_level=None, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys=OFF")

atexit.register(conn.close)
atexit.register(cursor.close)

version = read_file("/VERSION").rstrip()

# This tells us whether the migration has already happened.
check_sql = '''SELECT COUNT(*) AS count
               FROM pragma_table_info("tests")
               WHERE name = "code"'''

cursor.execute(check_sql)
check_result = cursor.fetchone()["count"]

if check_result > 0:
    print("***NotNeeded***")
else:
    with open("/migration_scripts/15_to_16.sql") as sql_file:
        sql_statements = sql_file.read().split(";")

    try:
        for sql in sql_statements:
            print(sql)
            cursor.executescript(sql)

        content.rebuild_exercises()
        content.rerun_submissions()
        print("***Success***")
    except:
        print(traceback.format_exc())
