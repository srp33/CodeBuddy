from BaseOtherHandler import *
from tornado.web import *
from helper import *

class LogoutHandler(BaseOtherHandler):
    def get(self):
        try:
            user_id_cookie = self.get_secure_cookie("user_id")
            if user_id_cookie:
                self.clear_cookie("user_id")

            #if self.in_production_mode():
                #self.redirect("https://accounts.google.com/Logout")
            #else:
            self.redirect("/")
        except Exception as inst:
            render_error(self, traceback.format_exc())

# See https://quanttype.net/posts/2020-02-05-request-id-logging.html