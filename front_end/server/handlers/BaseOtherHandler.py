from helper import *
from BaseRequestHandler import *
from tornado.web import RequestHandler
import traceback

class BaseOtherHandler(BaseRequestHandler):
    def get_current_user(self):
        user_id = super().get_current_user()

        if not user_id:
            return get_client_ip_address(self.request)

    def on_finish(self):
        try:
            log_page_access(self)
        except:
            print(f"Error occurred when attempting to log. {traceback.format_exc()}")
            pass

        super().on_finish()