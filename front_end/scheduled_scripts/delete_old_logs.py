# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

import glob
import os
import stat
import sys
import time

in_dir_path = sys.argv[1]

def is_old_file(file_path, days):
    age_in_seconds = time.time() - os.stat(file_path)[stat.ST_MTIME]
    age_in_days = age_in_seconds / 60 / 60 / 24
    return age_in_days > days

for f in glob.glob("{}/*".format(in_dir_path)):
    if is_old_file(f, 30):
        os.remove(f)