from tornado.web import *
from content import *

class DevelopmentLoginHandler(RequestHandler):
    def prepare(self):
        self.settings_dict = load_yaml_dict(read_file("/Settings.yaml"))
        self.content = Content(self.settings_dict)

    def get(self, target_path):
        if not target_path:
            target_path = ""

        self.render("devlogin.html", courses=self.content.get_courses(False), target_path=target_path)

    def post(self, target_path):
        try:
            user_id = self.get_body_argument("user_id")

            if user_id == "":
                self.write("Invalid user ID.")
            else:
                full_user_id = f'{user_id}@test.com'

                if not self.content.user_exists(full_user_id):
                    # Add static information for test user.
                    user_dict = {'name': f'{user_id} TestUser', 'given_name': user_id, 'family_name': 'TestUser', 'locale': 'en'}
                    self.content.add_user(full_user_id, user_dict)

                self.set_secure_cookie("user_id", full_user_id, expires_days=30)

                if not target_path:
                    target_path = "/"
                self.redirect(target_path)

        except Exception as inst:
            render_error(self, traceback.format_exc())

