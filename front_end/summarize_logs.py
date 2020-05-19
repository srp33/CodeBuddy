import gzip
import json
import sys

in_file_path = sys.argv[1]
summarized_file_path = sys.argv[2]

summary_dict = {}
if os.path.exists(summarized_file_path):
    with gzip.open(summarized_file_path) as summarized_file:
        summary_dict = json.loads(summarized_file.read().decode())

#INFO 200516 16:30:07 process Starting 4 processes
#INFO 200516 16:30:07 webserver Starting on port 9001...
#INFO 200516 16:30:12 web 304 GET /problem/NRZa/FyRE/Zocy (10.0.81.15) 60.51ms
#INFO 200516 16:30:12 web 200 GET /static/favicon-32x32.png (10.0.81.15) 0.92ms

# We use a set rather than a list because it's much faster
root_dirs_to_log = set(["course", "assignment", "problem", "check_problem"])
for line in in_file:
    line_items = line.decode().rstrip("\n").split(" ")

    if line_items[3] != "web":
        continue

    file_path = line_items[5]
    root_dir = file_path.split("/")[1]
    if root_dir in root_dirs_to_log:

    if file_path not in summary_dict:
        summary_dict[file_path] = {}

    #TODO: Record this based on the day (or day+hour), not global count.
    summary_dict[file_path] = summary_dict.setdefault(file_path, 0) + 1

with gzip.open(summarized_file_path, 'w') as summarized_file:
    if len(summary_dict) > 0:
        summarize_file.write(json.dumps(summary_dict))
