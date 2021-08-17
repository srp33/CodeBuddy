import atexit
import sqlite3
import sys
import traceback

sys.path.append('/app')
from helper import *
from content import *
from content_maria import *

settings_dict = load_yaml_dict(read_file("/Settings.yaml"))
content = Content(settings_dict)

version = read_file("/VERSION").rstrip()

# This tells us whether the migration has already happened.
check_sql = '''SELECT COUNT(*) AS count
               FROM pragma_table_info("tests")
               WHERE name = "go"'''

if content.fetchone(check_sql)["count"] > 0:
    print("***NotNeeded***")
else:
    with open("/migration_scripts/19_to_20.sql") as sql_file:
        sql_statements = sql_file.read().split(";")

    try:
        with open("/logs/progress.log", "w") as progress_file:
            for sql in sql_statements:
                progress_file.write(sql + "\n")
                content.execute(sql)

            run_command(f"touch {settings_dict['db_name'][:-3]}_dump.sql")
            progress_file.write(run_command("ls *dump.sql"))
            run_command("sqlite3 " + settings_dict['db_name'] + " .dump | python dump_for_mysql.py")
            progress_file.write("sqlite3 " + settings_dict['db_name'] + " .dump | python dump_for_mysql.py > " + settings_dict['db_name'][:-3] + "_dump.sql\n")
            progress_file.write(run_command("ls *dump.sql")  + "\n")
            progress_file.write(run_command("pwd"))

            # with open('file.sql', 'w') as make_db:
            #     make_db.write("CREATE DATABASE IF NOT EXISTS CodeBuddy")

            with open('CodeBuddy_dump.sql') as x:
                progress_file.write(x.read())

            progress_file.write('\n\n\n\n\n\incoming migration\n\n\n\n\n\n')

            run_command(f"mysql start")
            progress_file.write(run_command('''mysql select @@hostname;
show variables where Variable_name like "%host%" '''))

            run_command(f"mysql CREATE DATABASE CodeBuddy_mariadb")
            # run_command(f"mysql {settings_dict['db_name']_mariadb} > file.sql")
            run_command(f"mysql CodeBuddy_mariadb > CodeBuddy_dump.sql")
            # progress_file.write(f"mysql {settings_dict['db_name']}_mariadb > {settings_dict['db_name']}_dump.sql" + '\n')
            #
            # progress_file.write('post migration\n')
            content = Content_maria(settings_dict)
            progress_file.write("\n\n\n\n\n\n\n" + content.get_database_version())

        print("***Success***")

    except:
        print(traceback.format_exc())

        try:
            with open("/logs/progress.log", "a") as progress_file:
                progress_file.write(traceback.format_exc())
        except:
            pass
