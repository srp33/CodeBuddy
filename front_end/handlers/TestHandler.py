from tornado.web import *

class TestHandler(RequestHandler):
    def get(self):
        try:
            self.render("test.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

