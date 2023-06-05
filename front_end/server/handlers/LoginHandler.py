from BaseOtherHandler import *
from tornado.web import *
from helper import *

class LoginHandler(BaseOtherHandler):
    async def get(self):
        try:
            redirect_to_login(self, "/")
        except Exception as inst:
            render_error(self, traceback.format_exc())