# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

import glob
import gzip
import os
import re
import sys
import ujson

sys.path.append('/app/server')
from content import *
from helper import *

in_file_prefix = sys.argv[1]
summary_file_path = sys.argv[2]
archive_file_path = sys.argv[3]

content = Content()

# Read the existing summary if it exists.
summary_dict = {}
if os.path.exists(summary_file_path):
    with open(summary_file_path) as summary_file:
        summary_dict = ujson.loads(summary_file.read())

# We want the newest file (with no number at the end) to come first in the list.
in_file_paths = glob.glob(in_file_prefix + ".*") + [in_file_prefix]

# in_file_paths could still have a value even if the file doesn't exist
in_file_paths = [x for x in in_file_paths if os.path.exists(x)]

for in_file_path in in_file_paths:
    with open(in_file_path) as in_file:
        for line in in_file:
            timestamp_match = re.search(r"\[([\d\- \:]+)\]", line)

            if not timestamp_match:
                continue

            timestamp = timestamp_match.group(1)
            line_items = line.replace(f"[{timestamp}] ", "").rstrip("\n").split("\t")

            if len(line_items) < 5 or not line_items[1].startswith("/"):
                continue

            # Check for valid IP address
            ip_address = line_items[3]
            if not re.search(r"^(?:\d{1,3}\.){3}\d{1,3}$", ip_address):
                continue

            # Check for valid float pattern
            duration = line_items[4]
            if not re.search(r"^\d+\.\d+$", duration):
                continue

            user = ip_address if len(line_items) == 5 else line_items[5]

            # Change timestamp to reflect the day and hour
            timestamp = timestamp[:13].replace(" ", "-")

            path = line_items[1]
            path_root = re.search(r"^/([^/?]+)", path)
            
            if not path_root:
                continue
            
            path_root = path_root.group()
            path_root = f"{path_root} ({line_items[2]})"

            if path_root not in summary_dict:
                summary_dict[path_root] = {}

            if timestamp not in summary_dict[path_root]:
                summary_dict[path_root][timestamp] = {"hits": 0, "duration": 0.0, "user_hits": {}}

            summary_dict[path_root][timestamp]["hits"] += 1
            summary_dict[path_root][timestamp]["duration"] += float(duration)

            if user in summary_dict[path_root][timestamp]["user_hits"]:
                summary_dict[path_root][timestamp]["user_hits"][user] += 1
            else:
                summary_dict[path_root][timestamp]["user_hits"][user] = 1

if len(summary_dict) > 0:
    with open(summary_file_path, "w") as summary_file:
        summary_file.write(ujson.dumps(summary_dict, default=str))

with gzip.open(archive_file_path, "a") as archive_file:
    for in_file_path in in_file_paths:
        with open(in_file_path) as in_file:
            for line in in_file:
                archive_file.write(line.encode())

        os.remove(in_file_path)