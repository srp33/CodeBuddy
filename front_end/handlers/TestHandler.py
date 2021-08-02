import sys
sys.path.append("..")
from app.helper import *
from tornado.web import *
import traceback
class TestHandler(RequestHandler):
    def get(self):
        try:
            self.render("test.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

