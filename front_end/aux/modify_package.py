import json

file_path = "/static/package.json"

with open(file_path) as read_file:
    contents = read_file.read()
    contents_dict = json.loads(contents)
    contents_dict["scripts"]["css-build"] = "node-sass --omit-source-map-url sass/mystyles.scss css/mystyles.css"

with open(file_path, "w") as write_file:
    write_file.write(json.dumps(contents_dict, indent=2))
