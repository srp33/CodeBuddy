import re
import subprocess
import sys

code_file_path = sys.argv[1]
output_type = sys.argv[2]

output_file_path = "/sandbox/output"
error_file_path = "/sandbox/error"

error_file = open(error_file_path, "w")
output_file = None

try:
    if output_type == "txt":
        output_file = open(output_file_path, "w")
        #result = subprocess.run(f"python {code_file_path}", shell=True, stdout=output_file, stderr=error_file)
        result = subprocess.run(f"python {code_file_path}", shell=True, stdout=output_file, stderr=subprocess.PIPE)
    else:
        with open(code_file_path, "a") as code_file:
            render_code = f"""
from matplotlib import pyplot as my_plt_saver
my_plt_saver.savefig('{output_file_path}', format='jpg', dpi=150)
my_plt_saver.close()"""
            code_file.write(render_code)

        #result = subprocess.run(f"python {code_file_path}", shell=True, stdout=None, stderr=error_file)
        result = subprocess.run(f"python {code_file_path}", shell=True, stdout=None, stderr=subprocess.PIPE)

    if len(result.stderr) > 0:
        error = result.stderr.decode()

        # This makes the error message a little more user friendly.
        # It's a little hacky because the Python syntax could change.
        error = re.sub(r"\s*File \"/sandbox/code\", l(ine \d+),", r"\n  L\1:", error)
        error = error.replace(" in <module>", "")
        error_file.write(error)
except:
    error_file.write(traceback.format_exc())
finally:
    if output_file:
        output_file.close()
    error_file.close()
