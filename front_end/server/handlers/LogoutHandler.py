from BaseOtherHandler import *
from tornado.web import *
from helper import *

class LogoutHandler(BaseOtherHandler):
    def get(self):
        try:
            for cookie in self.request.cookies:
                self.clear_cookie(cookie)

            self.redirect("/")
        except Exception as inst:
            render_error(self, traceback.format_exc())

# See https://quanttype.net/posts/2020-02-05-request-id-logging.html