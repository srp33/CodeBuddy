import os
import re

if os.path.exists("txt_output"):
    output = ""

    with open("txt_output") as txt_file:
        for line in txt_file:
            line = line.lstrip()

            if line.startswith("Compiling test-project") or line.startswith("Finished dev") or line.startswith("Running `target/debug/test-project`"):
                continue

            output += line

    with open("txt_output", "w") as txt_file:
        txt_file.write(output)
