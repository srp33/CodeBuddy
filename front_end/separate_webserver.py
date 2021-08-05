import os

importDict = {
    'render_error': ['from helper import *'],
    '(RequestHandler)': ['from tornado.web import *'],
    'traceback': ['import traceback'],
    '(BaseUserHandler)': ['from BaseUserHandler import *'],
    'datetime': ['import datetime'],
    'GoogleOAuth2Mixin': ['from tornado.auth import GoogleOAuth2Mixin'],
    'logging': ['import logging'],
    'content': ['from content import *', 'settings_dict = load_yaml_dict(read_file("/Settings.yaml"))\ncontent = Content(settings_dict)'],
    'user_info_var': ['import contextvars', 'user_info_var = contextvars.ContextVar("user_info")'],
    'user_is_administrator_var': ['', 'user_is_administrator_var = contextvars.ContextVar("user_is_administrator")'],
    'user_instructor_courses_var': ['', 'user_instructor_courses_var = contextvars.ContextVar("user_instructor_courses")'],
    'user_assistant_courses_var': ['', 'user_assistant_courses_var = contextvars.ContextVar("user_assistant_courses")'],
}

with open('old_webserver.py') as ws:
    file = ws.read()
    file = file.split("class ")
    new_webserver = file[0]
    file = [f'class {file[i]}' for i in range(len(file)) if i != 0]
    end = file[-1].split('return True\n')[1]
    file[-1] = file[-1].split('if __name__ == "__main__":')[0]
    new_webserver = f'{new_webserver}\n\n{end}'

    if not os.path.isdir('handlers'):
        os.mkdir('handlers')
        with open("handlers/__init__.py", "w") as init:
            init.write("")
    for f in file:
        import_list_1 = ['from StaticFileHandler import *']
        import_list_2 = []
        for k,v in importDict.items():
            if k in f:
                import_list_1.append(v[0])
                if len(v) > 1:
                    import_list_2.append(v[1])

        with open(f'handlers/{f.split(" ")[1].split("(")[0]}.py', 'w') as curr:
            curr.write('import sys\nsys.path.append("..")\n')
            curr.write('\n'.join(import_list_1))
            curr.write('\n\n')
            curr.write('\n'.join(import_list_2))
            curr.write('\n\n')
            curr.write(f)
    with open(f'webserver.py', 'w') as nws:
        for f in file:
            nws.write(f'from {f.split(" ")[1].split("(")[0]} import *\n')
        nws.write('\n')
        nws.write(new_webserver)
