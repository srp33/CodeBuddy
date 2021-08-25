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
            # Execute migration script's sql commands
            for sql in sql_statements:
                progress_file.write(sql + "\n")
                content.execute(sql)

            progress_file.write('commence migration \n----------------------------------------------------------\n\n')

            # Dumps the current SQLite database into a sql file that is converted into MYSQL.
            sqlite_dump_name = content.dump_database()

            # Switch to content_mariadb.
            content = Content(settings_dict)

            with open(sqlite_dump_name) as db_dump:
                # These tables shouldn't be present in the current version, but if they slipped through, do not migrate them over to MariaDB.
                old_tables = ['course_registration', 'user_assignment_start', 'problems']

                create_statements = []
                other_statements = []

                missing_parantheses = None

                # Splits sql commands on semicolons that aren't inside strings
                for sql_command in re.split(r"(?!\B[`'][^`']*);(?![^`']*[`']\B)", db_dump.read()):
                    sql_command = sql_command.strip()

                    # Joins sql fragments together if needed.
                    if missing_parantheses is not None:
                        sql_command = f"{missing_parantheses};{sql_command}"

                    # If sql command is missing a closing paranthesis, flag it as a fragment and start scanning for the end.
                    if not sql_command.endswith(")"):
                        missing_parantheses = sql_command
                    else:
                        missing_parantheses = None
                        if "TABLE" in sql_command:
                            # Adds all create statements to a list
                            if 'CREATE TABLE' in sql_command:
                                # Excludes any table found in 'old_tables'
                                if all([f'`{table}`' not in sql_command for table in old_tables]):
                                    create_statements.append(sql_command)
                        else:
                            # Adds all other statements to a separate list
                            other_statements.append(sql_command)

                # Specifies order that create statements should be run in
                order = ['courses','users','assignments','exercises','submissions','tests','presubmissions','submission_outputs','help_requests','metadata','scores','course_registrations','permissions','user_assignment_starts']
                order =  [f"CREATE TABLE IF NOT EXISTS `{o}`" for o in order]
                ordered_create_statements = []

                # Provides error logging if the order list and create statements list are out of sync (I can't picture that this would happen anymore, but it's an important bug to check for)
                if len(order) != len(create_statements):
                    create_statements = [x.split(" (")[0] for x in create_statements]

                    greater = order if len(order) > len(create_statements) else create_statements
                    lesser = order if len(order) < len(create_statements) else create_statements
                    missing = list(set(greater) - set(lesser))

                    # Writes the missing statements in progress.log
                    for m in missing:
                        progress_file.write(f"missing: {m}" + "\n")

                    sys.exit(1)

                # Surely there's a cleaner, more efficient way to order the create statements but this is what I used
                for i in range(len(order)):
                    for j in range(len(create_statements)):
                        if create_statements[j].strip().startswith(order[i]):
                            ordered_create_statements.append(create_statements[j])
                            break

                # Temporarily allows adding of rows before the addition of rows they might reference as foreign keys
                content.execute("SET FOREIGN_KEY_CHECKS=0")

                for c in ordered_create_statements:
                    # Executes each create statement in order
                    progress_file.write(c + "\n")
                    content.execute(c)

                for o in other_statements:
                    # Executes all other statements
                    progress_file.write(o + "\n")
                    content.execute(o)

                # Updates metadata values and returns foreign_key_checks to on
                content.execute("INSERT INTO `metadata` VALUES(21);")
                content.execute("SET FOREIGN_KEY_CHECKS=1")

        print("***Success***")

    except:
        print(traceback.format_exc())

        with open("/logs/progress.log", "a") as progress_file:
            progress_file.write(traceback.format_exc())
