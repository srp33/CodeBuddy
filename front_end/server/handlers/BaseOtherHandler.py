from helper import *
from tornado.web import RequestHandler
import traceback

class BaseOtherHandler(RequestHandler):
    def on_finish(self):
        try:
            log_page_access(self)
        except:
            print(f"Error occurred when attempting to log. {traceback.format_exc()}")
            pass
