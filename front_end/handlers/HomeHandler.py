from tornado.web import *
import traceback
import contextvars
from helper import *


class HomeHandler(RequestHandler):
    def __init__(self):
        self.user_info_var = contextvars.ContextVar("user_info")
        self.user_is_administrator_var = contextvars.ContextVar("user_is_administrator")

    def prepare(self):
        try:
            user_id = self.get_secure_cookie("user_id")

            # Set context variables depending on whether the user is logged in.
            if user_id:
                user_id = user_id.decode()
                self.user_info_var.set(user_id)
            else:
                self.user_info_var.set(get_client_ip_address(self.request))
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def get(self):
        try:
            user_id = self.get_secure_cookie("user_id")

            if self.content.get_user_count() > 0 and not self.content.administrator_exists():
                if user_id:
                    self.content.add_admin_permissions(user_id.decode())
                    self.user_is_administrator_var.set(True)
                    self.redirect(f"/profile/courses/{user_id.decode()}")
                else:
                    if self.settings_dict["mode"] == "production":
                        self.set_secure_cookie("redirect_path", "/")
                        self.redirect("/login")
                    else:
                        self.redirect("/devlogin")
            else:
                if user_id:
                    self.redirect(f"/profile/courses/{user_id.decode()}")
                else:
                    self.render("home.html", mode=self.settings_dict["mode"], courses=self.content.get_available_courses(None))
        except Exception as inst:
            print(traceback.format_exc())
            render_error(self, traceback.format_exc())

