import re
import sys

file_path = sys.argv[1]
prefix = sys.argv[2]
suffix = sys.argv[3]

pattern = rf"{prefix} <copyright_statement>{suffix}[\W\w]+?{prefix} <\/copyright_statement>{suffix}\n\n"

with open(file_path) as the_file:
    text = the_file.read()
    text = re.sub(pattern, "", text, re.MULTILINE)

with open(file_path, "w") as the_file:
    the_file.write(text)
