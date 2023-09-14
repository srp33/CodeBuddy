# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

import os
import re

if os.path.exists("txt_output"):
    output = ""

    with open("txt_output") as txt_file:
        for line in txt_file:
            line = line.lstrip()

            if line.startswith("Compiling test-project") or line.startswith("Finished dev") or line.startswith("Running `target/debug/test-project`"):
                continue

            output += line

    with open("txt_output", "w") as txt_file:
        txt_file.write(output)
