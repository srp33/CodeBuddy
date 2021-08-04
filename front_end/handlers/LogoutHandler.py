from app.helper.helper import *
from tornado.web import *
import traceback
class LogoutHandler(RequestHandler):
    def get(self):
        try:
            self.clear_all_cookies()

            if settings_dict["mode"] == "production":
                self.redirect("https://accounts.google.com/Logout")
            else:
                self.redirect("/")
        except Exception as inst:
            render_error(self, traceback.format_exc())

# See https://quanttype.net/posts/2020-02-05-request-id-logging.html
