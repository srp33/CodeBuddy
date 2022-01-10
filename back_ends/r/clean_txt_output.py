import os
import re

output_lines = []

if os.path.exists("txt_output"):
    with open("txt_output") as output_file:
        for line in output_file:
            if line.startswith("Calls: "):
                continue
            if line == "Execution halted\n":
                continue

            line = re.sub(r"Error in parse\(text = code\) : <text>:\d+:0", "Error", line)
            line = re.sub(r"Error in eval\(parse\(text = code\)\) :", "Error:", line)

            output_lines += line

    with open("txt_output", "w") as output_file:
        output_file.write("".join(output_lines))
