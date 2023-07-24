# <copyright_statement>
#   CodeBuddy - computing-education software
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

import os
import re

if os.path.exists("txt_output"):
    with open("txt_output") as output_file:
        txt_output = output_file.read()

    txt_output = re.sub(r"Traceback \(most recent call last\)", r"Traceback (most recent call last)", txt_output)
    txt_output = re.sub(r"File \"code\", (line \d+)", r"Error on \1", txt_output)

    with open("txt_output", "w") as output_file:
        output_file.write(txt_output)
