from tornado.web import *
import traceback


class StaticFileHandler(RequestHandler):
    async def get(self, file_name):
        if file_name.endswith(".html"):
            try:
                self.render(file_name)
            except Exception as inst:
                render_error(self, traceback.format_exc())
        else:
            self.content_type = "text/css"
            read_mode = "r"

            if file_name.endswith(".js"):
                self.content_type = "text/javascript"
            elif file_name.endswith(".png"):
                self.content_type = "image/png"
                read_mode = "rb"
            elif file_name.endswith(".ico"):
                self.content_type = "image/x-icon"
                read_mode = "rb"
            elif file_name.endswith(".webmanifest"):
                self.content_type = "application/json"

            file_contents = read_file("/static/{}".format(file_name), mode=read_mode)

            self.set_header('Content-type', self.content_type)
            self.write(file_contents)

