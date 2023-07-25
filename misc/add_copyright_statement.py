import sys

file_path = sys.argv[1]
template_file_path = sys.argv[2]
prefix = sys.argv[3]
suffix = sys.argv[4]

with open(file_path, "w") as the_file:
    the_file.write(f"{prefix} <copyright_statement>{suffix}\n")

    with open(template_file_path) as template_file:
        for line in template_file:
            line = line.rstrip("\n")
            the_file.write(f"{prefix}   {line}{suffix}\n")

    the_file.write(f"{prefix} </copyright_statement>{suffix}\n\n")
