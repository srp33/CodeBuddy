from BaseOtherHandler import *
from tornado.web import *
from helper import *

class LoginHandler(BaseOtherHandler):
    async def get(self):
        try:
            # Google authentication is always enabled. BYU is only enabled if this (hidden) feature is specified.
            self.render("choose_login_option.html", byu_authentication=self.application.settings["byu_authentication"])
        except Exception as inst:
            render_error(self, traceback.format_exc())