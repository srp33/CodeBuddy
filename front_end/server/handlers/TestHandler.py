from tornado.web import *

class TestHandler(RequestHandler):
    def get(self):
        self.render("test.html")