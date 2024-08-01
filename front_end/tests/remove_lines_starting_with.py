import sys

in_file_path = sys.argv[1]
starting_text = sys.argv[2]
out_file_path = sys.argv[3]

with open(in_file_path) as in_file:
    with open(out_file_path, "w") as out_file:
        for line in in_file:
            if not line.startswith(starting_text):
                out_file.write(line)
