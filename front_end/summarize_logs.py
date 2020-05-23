import glob
import gzip
import json
import os
import shutil
import sys

in_file_prefix = sys.argv[1]
out_dir_path = sys.argv[2]
temp_file_path = sys.argv[3]

# This indicates the directory names of hits we want to log.
# We use a set rather than a list because it's much faster.
root_dirs_to_log = set(["", "course", "assignment", "problem", "check_problem", "edit_course", "edit_assignment", "edit_problem", "delete_course", "delete_assignment", "delete_problem", "import_course", "export_course"])

def update_summary_dict(summary_dict, timestamp, key, value):
    summary_dict[timestamp] = summary_dict.setdefault(timestamp, {})
    summary_dict[timestamp][key] = summary_dict[timestamp].setdefault(key, 0) + value

def create_timestamp(year, day, hour):
    return int(f"{year}{day}{hour}")

def save_summary(summary_dict, out_file_path):
    recent_timestamps = set(summary_dict.keys())

    # Find any previously summarized values that overlaps with what we just observed.
    if os.path.exists(out_file_path):
        shutil.copy(out_file_path, temp_file_path)

        with gzip.open(temp_file_path) as temp_file:
            with gzip.open(out_file_path, 'w') as out_file:
                out_file.write(temp_file.readline())

                for line in temp_file:
                    line_items = line.decode().rstrip("\n").split("\t")
                    if int(line_items[0]) in recent_timestamps:
                        update_summary_dict(summary_dict, int(line_items[0]), line_items[1], float(line_items[2]))
                    else:
                        out_file.write(line)
    else:
        with gzip.open(out_file_path, 'w') as out_file:
            out_file.write("Timestamp\tKey\tValue\n".encode())

    with gzip.open(out_file_path, 'a') as out_file:
        for timestamp, value_dict in sorted(summary_dict.items()):
            for key, value in sorted(value_dict.items()):
                out_file.write(f"{timestamp}\t{key}\t{value:.1f}\n".encode())

# We want the newest file (with no number at the end) to come list in the list.
in_file_paths = glob.glob(in_file_prefix + ".*") + [in_file_prefix]

hits_dict = {}
time_dict = {}
ip_dict = {}

for in_file_path in in_file_paths:
    if not os.path.exists(in_file_path):
        continue

    with open(in_file_path) as in_file:
        for line in in_file:
            line_items = line.rstrip("\n").split(" ")

            if line_items[3] != "web":
                continue

            file_path = line_items[6]
            root_dir = file_path.split("/")[1]
            if root_dir in root_dirs_to_log:
                #status = line_items[0]
                year = line_items[1][:4]
                day = line_items[1][4:]
                hour = line_items[2].split(":")[0]
                timestamp = create_timestamp(year, day, hour)
                ip_address = line_items[7].replace("(", "").replace(")", "")
                processing_milliseconds = float(line_items[8].replace("ms", ""))

                update_summary_dict(hits_dict, timestamp, file_path, 1)
                update_summary_dict(time_dict, timestamp, file_path, processing_milliseconds)
                update_summary_dict(ip_dict, timestamp, ip_address, 1)

hits_summary_file_path = f"{out_dir_path}/Hits.tsv.gz"
time_summary_file_path = f"{out_dir_path}/Time.tsv.gz"
ip_summary_file_path = f"{out_dir_path}/IP.tsv.gz"

save_summary(hits_dict, hits_summary_file_path)
save_summary(time_dict, time_summary_file_path)
save_summary(ip_dict, ip_summary_file_path)
