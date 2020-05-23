import sys
from helper import *

in_dir_path = sys.argv[1]

for f in glob.glob("{}/*".format(in_dir_path)):
    if is_old_file(f):
        os.remove(f)
