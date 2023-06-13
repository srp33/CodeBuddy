from BaseOtherHandler import *
from tornado.web import *
from helper import *

class LoginHandler(BaseOtherHandler):
    async def get(self):
        try:
            self.render("choose_login_option.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())