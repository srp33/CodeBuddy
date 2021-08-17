from tornado.web import *
import logging
from helper import *

class LogoutHandler(RequestHandler):
    def prepare(self):
        self.settings_dict = load_yaml_dict(read_file("/Settings.yaml"))

    def get(self):
        try:
            self.clear_all_cookies()

            if self.settings_dict["mode"] == "production":
                self.redirect("https://accounts.google.com/Logout")
            else:
                self.redirect("/")
        except Exception as inst:
            render_error(self, traceback.format_exc())

# See https://quanttype.net/posts/2020-02-05-request-id-logging.html
