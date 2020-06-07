import glob
import gzip
import json
import os
import shutil
import sys

in_file_prefix = sys.argv[1]
out_dir_path = sys.argv[2]
temp_file_path = sys.argv[3]

def update_summary_dict(summary_dict, statistic, timestamp, key, value):
    if statistic not in summary_dict:
        summary_dict[statistic] = {}

    summary_dict[statistic][timestamp] = summary_dict[statistic].setdefault(timestamp, {})
    summary_dict[statistic][timestamp][key] = summary_dict[statistic][timestamp].setdefault(key, 0) + value

def create_timestamp(year, month, day="", hour=""):
    return int(f"{year}{month}{day}{hour}")

def save_summaries(summary_dict, out_dir_path):
    for statistic, statistic_dict in summary_dict.items():
        out_file_path = f"{out_dir_path}/{statistic}.tsv.gz"
        recent_timestamps = set(statistic_dict.keys())

        # Find any previously summarized values that overlaps with what we just observed.
        if os.path.exists(out_file_path):
            shutil.copy(out_file_path, temp_file_path)

            with gzip.open(temp_file_path) as temp_file:
                with gzip.open(out_file_path, 'w') as out_file:
                    out_file.write(temp_file.readline())

                    for line in temp_file:
                        line_items = line.decode().rstrip("\n").split("\t")
                        timestamp = int(line_items[0])
                        if timestamp in recent_timestamps:
                            update_summary_dict(summary_dict, statistic, timestamp, line_items[1], float(line_items[2]))
                        else:
                            out_file.write(line)
        else:
            # Write header for output file
            with gzip.open(out_file_path, 'w') as out_file:
                out_file.write("Timestamp\tKey\tValue\n".encode())

        with gzip.open(out_file_path, 'a') as out_file:
            for timestamp, value_dict in sorted(statistic_dict.items()):
                for key, value in sorted(value_dict.items()):
                    out_file.write(f"{timestamp}\t{key}\t{value:.1f}\n".encode())

# We want the newest file (with no number at the end) to come list in the list.
in_file_paths = glob.glob(in_file_prefix + ".*") + [in_file_prefix]

# This indicates the directory names of hits we want to log.
# We use a set rather than a list because it's much faster.
root_dirs_to_log = set(["/", "course", "assignment", "problem", "check_problem", "edit_course", "edit_assignment", "edit_problem", "delete_course", "delete_assignment", "delete_problem", "view_answer", "import_course", "export_course"])

summary_dict = {}

for in_file_path in in_file_paths:
    # in_file_paths could still have a value even if the file doesn't exist
    if not os.path.exists(in_file_path):
        continue

    with open(in_file_path) as in_file:
        for line in in_file:
            line_items = line.rstrip("\n").split(" ")

            if line_items[3] != "web":
                continue

            file_path = line_items[6]
            root_dir = file_path.split("/")[1]
            if root_dir == "":
                root_dir = "/"

            if root_dir in root_dirs_to_log:
                #status = line_items[0]
                year = line_items[1][:2]
                month = line_items[1][2:4]
                day = line_items[1][4:]
                hour = line_items[2].split(":")[0]
                day_timestamp = create_timestamp(year, month, day)
                hour_timestamp = create_timestamp(year, month, day, hour)
                ip_address = line_items[7].replace("(", "").replace(")", "")
                processing_milliseconds = float(line_items[8].replace("ms", ""))
                user_id = line_items[9] # Will be IP address if user not logged in.
                #if user_id == "-":
                #    user_id = ip_address

                # Aggregated by hour:
                #   Total number of hits per specific page from *any* user.
                #   Load duration per specific page from *any* user.
                # Aggregated by day:
                #   Total number of hits to *any* page per user.

                update_summary_dict(summary_dict, "HitsAnyUser", hour_timestamp, file_path, 1)
                update_summary_dict(summary_dict, "LoadDuration", hour_timestamp, file_path, processing_milliseconds)
                update_summary_dict(summary_dict, "HitsPerUser", day_timestamp, user_id, 1)

save_summaries(summary_dict, out_dir_path)
