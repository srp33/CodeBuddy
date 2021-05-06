import atexit
import sqlite3
import sys
import traceback
sys.path.append('/app')
from helper import *

# Example value: 8_to_9
migration_numbers = sys.argv[1]

# There must be two SQL files for each migration. One checks
# whether the migration has already occurred. The other modifies the
# database. Using the example value, these files would be called
# 8_to_9_check.sql and 8_to_9_migrate.sql, respectively.
# The check query must have a column called "count" in the select
# statement.
check_file_path = f"/migration_scripts/{migration_numbers}_check.sql"
migrate_file_path = f"/migration_scripts/{migration_numbers}_migrate.sql"

settings_dict = load_yaml_dict(read_file("/Settings.yaml"))

conn = sqlite3.connect(f"/database/{settings_dict['db_name']}", isolation_level=None, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys=OFF")

atexit.register(conn.close)
atexit.register(cursor.close)

check_sql = read_file(check_file_path)
cursor.execute(check_sql)

if cursor.fetchone()["count"] > 0:
    print("***NotNeeded***")
else:
    sql_statements = read_file(migrate_file_path).split(";")

    try:
        for sql in sql_statements:
            print(sql)
            cursor.executescript(sql)
        print("***Success***")
    except:
        print(traceback.format_exc())
