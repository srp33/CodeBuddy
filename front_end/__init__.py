import sys
import importlib
import os
import re
import glob

# Gets all module names ending with .py
modules = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))

# Gets only Handler names (ie, those with uppercase characters in them)
modules = [ os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and bool(re.match(r'.*[A-Z].*', f)) ]

# Imports each module along with all of its functions
for lib in modules:
    globals()[lib] = importlib.import_module(lib)
    names = [x for x in globals()[lib].__dict__ if not x.startswith("_")]
    globals().update({k: getattr(globals()[lib], k) for k in names})
