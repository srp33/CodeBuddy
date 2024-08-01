import sys

in_file_path = sys.argv[1]
out_file_path = sys.argv[2]

with open(in_file_path) as in_file:
    text = in_file.read()

text = text.replace("../VERSION", "VERSION")
text = text.replace("CodeBuddy.db", "database/CodeBuddy.db")

with open(out_file_path, "w") as out_file:
    out_file.write(text)
