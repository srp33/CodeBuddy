import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

from content import *
from helper import *

sql_file_path = "test_database_query.sql"
db_file_path = "database/CodeBuddy.db"
tsv_file_path = "/tmp/test_database_query.tsv"

sql = read_file(sql_file_path)

conn = sqlite3.connect(
        db_file_path,
        isolation_level = None,
        detect_types = sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES,
        timeout = 30,
    )

cursor = conn.cursor()

num_rows = 0

try:
    cursor.execute(sql)
    results = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]

    with open(tsv_file_path, "w") as tsv_file:
        column_names = [description[0] for description in cursor.description]
        out_header_row = "\t".join(column_names)
        print(out_header_row)
        tsv_file.write(out_header_row + "\n")

        for row in results:
            out_row = "\t".join([str(x) for x in row])
            print(out_row)
            tsv_file.write(out_row + "\n")

            num_rows += 1
except:
    print(traceback.format_exc())
finally:
    cursor.close()
    conn.close()

print(f"# rows: {num_rows}")
print(f"Results are in {tsv_file_path}")
