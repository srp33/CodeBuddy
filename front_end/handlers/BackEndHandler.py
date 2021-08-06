from helper import *
from tornado.web import *
import traceback
import logging


class BackEndHandler(RequestHandler):
    def prepare(self):
        self.settings_dict = load_yaml_dict(read_file("/Settings.yaml"))

    def get(self, back_end):
        try:
            self.write(json.dumps(settings_dict["back_ends"][back_end]))
        except Exception as inst:
            logging.error(self, traceback.format_exc())
            self.write(json.dumps({"Error": "An error occurred."}))

