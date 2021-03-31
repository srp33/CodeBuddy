import os
import re
import subprocess
import sys
import traceback

code_file_path = sys.argv[1]
test_code_file_path = sys.argv[2]
output_type = sys.argv[3]

if output_type == "jpg":
    with open(code_file_path, "a") as code_file:
        code_file.write(f"""
from matplotlib import pyplot as my_plt_saver
my_plt_saver.savefig('{output_file_path}', format='jpg', dpi=150)
my_plt_saver.close()""")

if os.path.exists(test_code_file_path):
    with open(test_code_file_path) as test_code_file:
        test_code = "\n\n" + test_code_file.read()

    with open(code_file_path, "a") as code_file:
        code_file.write(test_code)



result = subprocess.run(f"python {code_file_path}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()

# This makes the error message a little more user friendly.
result = re.sub(r"Traceback \(most recent call last\)", r"Traceback (most recent call last)", result)
print(re.sub(r"File \"\/sandbox\/code\", (line \d+)", r"Error on \1", result))
