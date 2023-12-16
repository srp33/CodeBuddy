# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

import os
import re

output_lines = []

if os.path.exists("txt_output"):
    with open("txt_output") as output_file:
        file_contents = output_file.read()

        # Remove output of read_* packages from readr package.
        #file_contents = re.sub(r"Parsed with column specification:\ncols\(\n[\w\W]+?\n\)\n", "", file_contents)
        #file_contents = re.sub(r"See spec(.+?) for full column specifications.\n", "", file_contents)
        file_contents = re.sub(r"Rows: \d+ Columns: \d+[\w\W]+?to quiet this message.\n", "", file_contents)

        for line in file_contents.split("\n"):
            if line.startswith("Calls: "):
                continue
            if line.startswith("Joining with `"):
                continue
            if line == "Execution halted\n":
                continue
            if line == "Saving 7 x 7 in image":
                continue

            line = re.sub(r"Error in parse\(text = code\) : <text>:\d+:0", "Error", line)
            line = re.sub(r"Error in eval\(parse\(text = code\)\) :", "Error:", line)

            output_lines.append(line.lstrip())

    with open("txt_output", "w") as output_file:
        output_file.write("\n".join(output_lines))
