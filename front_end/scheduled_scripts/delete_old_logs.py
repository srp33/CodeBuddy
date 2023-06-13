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