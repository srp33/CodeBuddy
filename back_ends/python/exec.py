import os
import re
import subprocess
import sys
import traceback
import glob

output_type = sys.argv[1]

result = ''
if os.path.exists("verification_code"):
    result = subprocess.run("python verification_code", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
    if len(result) > 0:
        print(result)
        sys.exit()

os.chdir("tests")

for test_id in "*":
    if output_type == "jpg":
        with open("code") as code_file:
            code = code_file.read()

            code = f"""
from matplotlib import pyplot as my_plt_saver
my_plt_saver.savefig('test_image_output_{i}', format='jpg', dpi=150)
my_plt_saver.close()""" + code

        with open("code", "w") as code_file:
            code_file.write(code)

    result = subprocess.run(f"python code", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()

    # This makes the error message a little more user friendly.
    result = re.sub(r"Traceback \(most recent call last\)", r"Traceback (most recent call last)", result)
    result = re.sub(r"File \"\/sandbox\/code\", (line \d+)", r"Error on \1", result)

    if result != "":
        if output_type == "jpg":
            with open(f"{test_id}/image_output", "w") as test_output:
                test_output.write(result)
        else:
            with open(f"{test_id}/text_output", "w") as test_output:
                test_output.write(result)
