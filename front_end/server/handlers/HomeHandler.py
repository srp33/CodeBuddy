from BaseOtherHandler import *
from tornado.web import *
import contextvars
from content import *
from helper import *

class HomeHandler(BaseOtherHandler):
    def prepare(self):
        self.user_info_var = contextvars.ContextVar("user_info")
        self.user_is_administrator_var = contextvars.ContextVar("user_is_administrator")
        self.settings_dict = load_yaml_dict(read_file("../Settings.yaml"))
        self.content = Content(self.settings_dict)

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
                    redirect_to_login(self, "/")
            else:
                if user_id:
                    self.redirect(f"/profile/courses/{user_id.decode()}")
                else:
                    self.render("home.html", mode=self.settings_dict["mode"], courses=self.content.get_available_courses(None))
        except Exception as inst:
            print(traceback.format_exc())
            render_error(self, traceback.format_exc())
