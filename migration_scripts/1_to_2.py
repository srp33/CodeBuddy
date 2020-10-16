import atexit
from helper import *
import sqlite3

settings_dict = load_yaml_dict(read_file("/Settings.yaml"))

conn = sqlite3.connect(f"/database/{settings_dict['db_name']}", isolation_level=None, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
conn.row_factory = sqlite3.Row
cursor = self.conn.cursor()
cursor.execute("PRAGMA foreign_keys=ON")

atexit.register(conn.close)
atexit.register(cursor.close)

version = read_file("/VERSION")

check_sql = '''SELECT COUNT(*)
               FROM pragma_table_info("problems")
               WHERE name = "expected_text_output"'''

cursor.execute(check_sql)
check_result = cursor.fetchone()
if check_result == 0:
    print("Need to migrate")
else:
    print("Don't need to migrate")
sys.exit(0)

alter_sql_list = ['ALTER TABLE problems RENAME COLUMN expected_output TO expected_text_output',
              'ALTER TABLE problems ADD COLUMN expected_image_output text NOT NULL DEFAULT "',
              'ALTER TABLE submissions RENAME COLUMN code_output TO text_output',
              'ALTER TABLE submissions ADD COLUMN image_output text NOT NULL DEFAULT ""',
              '''UPDATE problems
                 SET expected_image_output = expected_text_output
                 WHERE output_type = "jpg"''',
              '''UPDATE problems
                 SET expected_text_output = ""
                 WHERE output_type = "jpg"''',
              '''UPDATE submissions
                 SET image_output = text_output
                 WHERE problem_id IN (SELECT problem_id FROM problems WHERE output_type = "jpg")''',
              '''UPDATE submissions
                 SET text_output = ""
                 WHERE problem_id IN (SELECT problem_id FROM problems WHERE output_type = "jpg")'''
             ]

for sql in alter_sql_list:
    print(sql)
    cursor.execute(sql)


#Create a copy of the database before changing anything. Delete it if successful. Roll it back if not.
#Put this logic as well as logic to check whether migration is needed in webserver.py or content.py.
#TODO: Change this to a Python script. Look at content.py for example code.
#TODO: Make sure it works when run the migrate script.
#TODO: Make sure it works when you build the database from scratch, too.
#TODO: Test production database in dev.
#Remove error_occurred column from submissions?
