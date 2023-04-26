from BaseOtherHandler import *
from tornado.web import *
from helper import *

class LoginHandler(BaseOtherHandler):
    def get(self):
        try:
            self.settings_dict = load_yaml_dict(read_file("../Settings.yaml"))
            redirect_to_login(self, "/")
        except Exception as inst:
            render_error(self, traceback.format_exc())