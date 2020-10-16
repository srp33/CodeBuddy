import fileinput

for line in fileinput.input():
    line = line.rstrip("\n")

    if line.startswith("Calls: "):
        continue
    if line == "Execution halted":
        continue

    line = re.sub(r"Error in parse\(text = code\) : <text>:\d+:0", "Error", line)
    line = re.sub(r"Error in eval\(parse\(text = code\)\) :", "Error:", line)

    print(line)
