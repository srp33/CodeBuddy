from tornado.web import *

class TestHandler(RequestHandler):
    async def get(self):
        self.render("test.html")