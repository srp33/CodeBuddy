from content import *
from helper import *
from tornado.web import RequestHandler

class BaseRequestHandler(RequestHandler):
    ###############################################
    # Overriding functions
    ###############################################

    def prepare(self):
        super().prepare()

        self.settings_dict = load_yaml_dict(read_file("../Settings.yaml"))
        self.content = Content()

    def get_current_user(self):
        user_id = self.get_secure_cookie("user_id")

        if user_id:
            return user_id.decode()

    ###############################################
    # Helper functions
    ###############################################

    def in_production_mode(self):
        return self.settings_dict["mode"] == "production"