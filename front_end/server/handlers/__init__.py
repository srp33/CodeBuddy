# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

import sys
import importlib
import os
import re
import glob


current_dir = os.path.dirname(__file__)

sys.path.append(current_dir)
# Gets all module names ending with .py
modules = glob.glob(os.path.join(current_dir, "*.py"))

# Gets only Handler names (ie, those with uppercase characters in them)
modules = [ os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and bool(re.match(r'.*[A-Z].*', f)) ]

# Imports each module along with all of its functions
for lib in modules:
    globals()[lib] = importlib.import_module(lib)
    names = [x for x in globals()[lib].__dict__ if not x.startswith("_")]
    globals().update({k: getattr(globals()[lib], k) for k in names})
