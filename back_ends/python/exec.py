import os
import re
import subprocess
import sys
import traceback

code_file_path = sys.argv[1]
tests_dir_path = sys.argv[2]
check_code_file_path = sys.argv[3]
output_type = sys.argv[4]

result = ''
if os.path.exists(check_code_file_path):
    result = subprocess.run(f"python {check_code_file_path}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
    if len(result) > 0:
        print(result)
        sys.exit()

if os.path.isdir(tests_dir_path):
    if output_type == "txt":
        for test in os.listdir(tests_dir_path):
            test_code_path = tests_dir_path + test
            result = subprocess.run(f"python {test_code_path}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
            result = re.sub(r"Traceback \(most recent call last\)", r"Traceback (most recent call last)", result)
            i = test_code_path.split("_")[1]

            filename = f"{tests_dir_path}outputs/test_{i}/text_output"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as test_output:
                test_output.write(result)
    else:
        for test in os.listdir(tests_dir_path):
            test_code_path = tests_dir_path + test

            i = test_code_path.split("_")[1]
            filename = f"{tests_dir_path}outputs/test_{i}/image_output"

            with open(test_code_path, "a") as test_file:
                test_file.write(f"""
from matplotlib import pyplot as my_plt_saver
my_plt_saver.savefig('test_image_output_{i}', format='jpg', dpi=150)
my_plt_saver.close()""")

            result = subprocess.run(f"python {test_code_path}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
            result = re.sub(r"Traceback \(most recent call last\)", r"Traceback (most recent call last)", result)

            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as test_output:
                test_output.write(result)

if output_type == "jpg":
    with open(code_file_path, "a") as code_file:
        code_file.write(f"""
from matplotlib import pyplot as my_plt_saver
my_plt_saver.savefig('image_output', format='jpg', dpi=150)
my_plt_saver.close()""")

result = subprocess.run(f"python {code_file_path}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()

# This makes the error message a little more user friendly.
result = re.sub(r"Traceback \(most recent call last\)", r"Traceback (most recent call last)", result)
print(re.sub(r"File \"\/sandbox\/code\", (line \d+)", r"Error on \1", result))
