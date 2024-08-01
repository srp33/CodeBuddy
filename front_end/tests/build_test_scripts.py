import glob
import json
import os
import sys

def add_imports(file_path, import_statements):
    with open(file_path) as the_file:
        for line in the_file:
            if (line.startswith("from") and not line.startswith("from Base") and not line.startswith("from content") and not line.startswith("from helper") and not line.startswith("from imgcompare")) or line.startswith("import"):
                import_statements.add(line)

def save_script(file_path, test_file):
    with open(file_path) as the_file:
        for line in the_file:
            if not line.startswith("from") and not line.startswith("import") and not line.startswith("#") > 0:
                # These customizations allow us to run the server in test mode.
                line = line.replace("../Settings.yaml", "Settings.yaml")
                line = line.replace("../back_ends", "back_ends")
                line = line.replace("self.get_secure_cookie(", "self.get_cookie(")
                line = line.replace(", max_age_days=max_age_days", "")
                line = line.replace("user_id.decode()", "user_id")
                line = line.replace(" datetime.now(timezone.utc)", " datetime.datetime.now(timezone.utc)")

                test_file.write(line)

handler_url_paths_dict = {}
with open("server/webserver.py") as ws_file:
    for line in ws_file:
        line = line.strip()

        if line.startswith("url("):
            part1 = line.split("url(r\"")[1]
            parts2 = part1.split("\", ")
            handler = parts2[1].split(",")[0]

            url_path_parts = [x for x in parts2[0].split("/")[1:] if x != ""]

            url_path = f"/{handler}"

            if len(url_path_parts) > 1:
                url_path += "/" + "/".join(url_path_parts[1:])

            handler_url_paths_dict[handler] = url_path

other_script_file_paths = ["server/content.py", "server/helper.py", "server/imgcompare.py"]
base_handler_file_paths = ["server/handlers/BaseRequestHandler.py", "server/handlers/BaseOtherHandler.py", "server/handlers/BaseUserHandler.py"]

handler_file_paths = sorted(glob.glob("server/handlers/*Handler.py"))
handler_file_paths = [x for x in handler_file_paths if not os.path.basename(x).startswith("Base") and not os.path.basename(x).startswith("GoogleLogin") and not os.path.basename(x).startswith("CASLogin")]

handler_class_names = []
import_statements = set()

# Find all the import statements in all the handlers.
# Also find all the non-base class names.

for other_script_file_path in other_script_file_paths:
    add_imports(other_script_file_path, import_statements)

for handler_file_path in handler_file_paths:
    handler_class_name = os.path.basename(handler_file_path).replace(".py", "")
    handler_class_names.append(handler_class_name)
    add_imports(handler_file_path, import_statements)

for handler_file_path in base_handler_file_paths:
    add_imports(handler_file_path, import_statements)

import_statements.add("import tornado.ioloop\n")
import_statements.add("import tornado.web\n")
import_statements.add("from tornado.routing import URLSpec as url\n")
import_statements.add("import ui_methods\n")

import_statements = sorted(import_statements)

with open("app.py", "w") as test_file:
    # Save the import statements to the test script.
    for i_s in import_statements:
        test_file.write(i_s)
    test_file.write("\n")

    # Save the content and helper scripts to the test script
    for other_script_file_path in other_script_file_paths:
        save_script(other_script_file_path, test_file)

    # Save the base handlers to the test script.
    for handler_file_path in base_handler_file_paths:
        save_script(handler_file_path, test_file)

    # Save the other handlers to the test script.
    for handler_file_path in handler_file_paths:
        save_script(handler_file_path, test_file)

    test_file.write("\n\n")

    test_file.write("def make_app():\n")
    test_file.write("\tapplication = tornado.web.Application([\n")

    for h_c_n in handler_class_names:
        test_file.write(f"\t\turl(r'{handler_url_paths_dict[h_c_n]}', {h_c_n}),\n")

    test_file.write("\t\t], autoescape=None, debug=True, ui_methods=ui_methods)\n\n")

    test_file.write("\tsecrets_dict = load_yaml_dict(read_file('secrets/front_end.yaml'))\n")
    test_file.write("\tapplication.settings['cookie_secret'] = secrets_dict['cookie']\n")

    with open("create_database.py") as db_file:
        test_file.write(db_file.read().replace("    ", "\t"))

    test_file.write("\treturn application\n\n")

    #with open("start_web_server_code.py") as start_file:
    #    test_file.write(start_file.read())

with open("test_app.py", "w") as test_file:
    test_file.write("import tornado.ioloop\n")
    test_file.write("import tornado.web\n")
    test_file.write("import tornado.testing\n")
    test_file.write("import tornado.httpclient\n")
    test_file.write("import unittest\n")
    test_file.write("from app import make_app\n\n")
    test_file.write("class TestMyApp(tornado.testing.AsyncHTTPTestCase):\n")
    test_file.write("\tdef get_app(self):\n")
    test_file.write("\t\treturn make_app()\n\n")

    with open("handler_tests.dat") as dat_file:
        handler_tests_data = json.load(dat_file)

    test_file.write("\tdef test_handlers(self):\n")
    test_file.write("\t\tprint('Running tests:')\n")

    for row in handler_tests_data:
        handler = row[0]
        path = row[1]
        text_to_match = row[2]

        url = f"/{handler}"

        if path != "":
            url += f"/{path}"

        test_file.write(f"\t\theaders = tornado.httputil.HTTPHeaders()\n")
        test_file.write(f"\t\tresponse = self.fetch('{url}', headers=" + "{'Cookie': 'user_id=test_student'})\n")
        test_file.write(f"\t\tprint('  {handler}')\n")
        test_file.write(f"\t\tfound = \"" + text_to_match + "\" in response.body.decode()\n")
        test_file.write(f"\t\tif found:\n")
        test_file.write(f"\t\t\tprint(\"    '" + text_to_match + "' was found.\")\n")
        test_file.write(f"\t\telse:\n")
        test_file.write(f"\t\t\tprint(\"    '" + text_to_match + "' was NOT found.\")\n")
        test_file.write(f"\t\tself.assertTrue(found)\n\n")
        test_file.write(f"\t\tself.assertEqual(response.code, 200)\n\n")

    test_file.write("if __name__ == '__main__':\n")
    test_file.write("\tunittest.main()\n")
