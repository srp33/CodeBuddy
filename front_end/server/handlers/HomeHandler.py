from BaseOtherHandler import *
from tornado.web import *
from content import *
from helper import *

class HomeHandler(BaseOtherHandler):
    def get(self):
        try:
            user_id = self.get_secure_cookie("user_id")

            if user_id:
                self.redirect(f"/courses")
            else:
                self.render("home.html")
        except Exception as inst:
            print(traceback.format_exc())
            render_error(self, traceback.format_exc())