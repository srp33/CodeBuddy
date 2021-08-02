import os

importDict = {
    'render_error': 'from .helper import *',
    'content': 'from .content import *',
    '(RequestHandler)': 'from tornado.web import *',
    'traceback': 'import traceback',
    '(BaseUserHandler)': 'from BaseUserHandler import *',
    'datetime': 'import datetime'
}

with open('webserver.py') as ws:
    file = ws.read()
    file = file.split("class ")
    new_webserver = file[0]
    file = [f'class {file[i]}' for i in range(len(file)) if i != 0]
    end = file[-1].split('return True\n')[1]
    file[-1] = file[-1].split('if __name__ == "__main__":')[0]
    new_webserver = f'{new_webserver}\n\n{end}'
    if not os.path.isdir('handlers'):
        os.mkdir('handlers')
    for f in file:
        import_list = []
        for k,v in importDict.items():
            if k in f:
                import_list.append(v)

        with open(f'handlers/{f.split(" ")[1].split("(")[0]}.py', 'w') as curr:
            curr.write('\n'.join(import_list))
            curr.write('\n')
            curr.write(f)
    with open(f'new_webserver.py', 'w') as nws:
        for f in file:
            nws.write(f'from handlers.{f.split(" ")[1].split("(")[0]} import *\n')
        nws.write('\n')
        nws.write(new_webserver)

