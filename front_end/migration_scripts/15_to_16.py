import atexit
import sqlite3
import sys
import traceback

sys.path.append('/app')
from helper import *
from content import *

settings_dict = load_yaml_dict(read_file("/Settings.yaml"))
content = ContentSQLite(settings_dict)

version = read_file("/VERSION").rstrip()

# This tells us whether the migration has already happened.
check_sql = '''SELECT COUNT(*) AS count
               FROM pragma_table_info("tests")
               WHERE name = "code"'''

if content.fetchone(check_sql)["count"] > 0:
    print("***NotNeeded***")
else:
    with open("/migration_scripts/15_to_16.sql") as sql_file:
        sql_statements = sql_file.read().split(";")

    try:
        with open("/logs/progress.log", "a") as progress_file:
            for sql in sql_statements:
                progress_file.write(sql + "\n")
                content.execute(sql)

        content.rebuild_exercises()
        content.rerun_submissions()
        print("***Success***")
    except:
        print(traceback.format_exc())

        try:
            with open("/logs/progress.log", "a") as progress_file:
                progress_file.write(traceback.format_exc())
        except:
            pass
