import os
import re

output_lines = []

if os.path.exists("txt_output"):
    with open("txt_output") as output_file:
        file_contents = output_file.read()

        # Remove output of read_* packages from readr package.
        file_contents = re.sub(r"Parsed with column specification:\ncols\(\n[\w =\(\),_\.\n]+?\n\)\n", "", file_contents)
        file_contents = re.sub(r"See spec(.+?) for full column specifications.\n", "", file_contents)

        for line in file_contents.split("\n"):
            if line.startswith("Calls: "):
                continue
            if line.startswith("Joining, by ="):
                continue
            if line == "Execution halted\n":
                continue
            if line == "Saving 7 x 7 in image":
                continue

            line = re.sub(r"Error in parse\(text = code\) : <text>:\d+:0", "Error", line)
            line = re.sub(r"Error in eval\(parse\(text = code\)\) :", "Error:", line)

            output_lines.append(line.lstrip())

    with open("txt_output", "w") as output_file:
        output_file.write("\n".join(output_lines))
