import atexit
import sqlite3
import sys
import traceback

sys.path.append('/app')
from helper import *
from content import *
from content_maria import *

settings_dict = load_yaml_dict(read_file("/Settings.yaml"))
content = ContentSQLite(settings_dict)

version = read_file("/VERSION").rstrip()

# This tells us whether the migration has already happened.
check_sql = '''SELECT COUNT(*) AS count
               FROM pragma_table_info("tests")
               WHERE name = "go"'''

if content.fetchone(check_sql)["count"] > 0:
    print("***NotNeeded***")
else:
    with open("/migration_scripts/20_to_21.sql") as sql_file:
        sql_statements = sql_file.read().split(";")

    try:
        with open("/logs/progress.log", "w") as progress_file:
            for sql in sql_statements:
                progress_file.write(sql + "\n")

                content.execute(sql)

            sqlite_dump = content.dump_database()

            content = Content(settings_dict)

            with open(sqlite_dump) as db_dump:
                create_statements = []
                other_statements = []

                missing_parantheses = None
                for c in re.split(r"(?!\B[`'][^`']*);(?![^`']*[`']\B)", db_dump.read()):
                    s = c.strip()

                    if missing_parantheses is not None:
                        s = f"{missing_parantheses};{s}"

                    if not s.endswith(")"):
                        missing_parantheses = s
                    else:
                        missing_parantheses = None
                        if "TABLE" in s:
                            if 'CREATE TABLE' in s:
                                if "INSERT INTO " in s:
                                    create_statements.append(s.split(';')[0])
                                    other_statements.append(s.split(';')[1])
                                else:
                                    create_statements.append(s)
                        else:
                            other_statements.append(s)

                order = ['courses','users','assignments','exercises','problems','submissions','tests','presubmissions','submission_outputs','help_requests','metadata','scores','course_registrations','permissions','user_assignment_starts']
                order =  [f"CREATE TABLE IF NOT EXISTS `{o}`" for o in order]
                create = []

                if len(order) != len(create_statements):
                    sys.exit(1)

                for i in range(len(order)):
                    for j in range(len(create_statements)):
                        if create_statements[j].strip().startswith(order[i]):
                            create.append(create_statements[j])
                            break

                content.execute("SET FOREIGN_KEY_CHECKS=0")

                for c in create:
                    content.execute(c)

                for o in other_statements:
                    content.execute(o)

                content.execute("INSERT INTO `metadata` VALUES(21);")
                content.execute("SET FOREIGN_KEY_CHECKS=1")

            progress_file.write(f"current db version post migration: {str(content.get_database_version())}")

        print("***Success***")

    except:
        print(traceback.format_exc())

        try:
            with open("/logs/progress.log", "a") as progress_file:
                progress_file.write(traceback.format_exc())
        except:
            pass
