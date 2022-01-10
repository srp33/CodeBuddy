import os
import re

if os.path.exists("txt_output"):
    with open("txt_output") as output_file:
        txt_output = output_file.read()

    txt_output = re.sub(r"Traceback \(most recent call last\)", r"Traceback (most recent call last)", txt_output)
    txt_output = re.sub(r"File \"code\.py\", (line \d+)", r"Error on \1", txt_output)

    with open("txt_output", "w") as output_file:
        output_file.write(txt_output)
