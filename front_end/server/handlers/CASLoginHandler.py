from BaseOtherHandler import *
from tornado.web import *
from tornado.auth import GoogleOAuth2Mixin
from content import *

# https://github.com/apereo/cas-sample-python-webapp/blob/master/app.py
# See https://djangocas.dev/blog/python-cas-flask-example/
class CASLoginHandler(BaseOtherHandler):
    async def get(self):
        try:
            if self.in_production_mode():
                service_url = f"https://{self.settings_dict['domain']}/login?next=%2Flogin"
            else:
                raise Exception("You cannot authenticate with CAS in development mode")
                #service_url="http://codebuddy.ls.byu.edu:8008/login?next=%2Flogin"

            server_url = "https://cas.byu.edu/cas/"

            # Moved this here so we can run it locally without having CAS installed.
            from cas import CASClient
            cas_client = CASClient(version=3, service_url=service_url, server_url=server_url)

            ticket = self.get_argument('ticket', False)
            if not ticket:
                cas_login_url = cas_client.get_login_url()
                self.redirect(cas_login_url)

            user_id, attributes, pgtiou = cas_client.verify_ticket(ticket)

            if not user_id:
                return

            user_dict = {"name": attributes["preferredFirstName"] + " " + attributes["preferredSurname"], "given_name": attributes["preferredFirstName"], "family_name": attributes["preferredSurname"], "locale": "en", "email_address": attributes["emailAddress"]}

            if self.content.user_exists(user_id):
                # Update user with current information when they already exist.
                self.content.update_user(user_id, user_dict)
            else:
                # Store current user information when they do not already exist.
                self.content.add_user(user_id, user_dict)

            self.set_secure_cookie("user_id", user_id, expires_days=30)

            redirect_path = self.get_secure_cookie("redirect_path")
            self.clear_cookie("redirect_path")
            if not redirect_path:
                redirect_path = "/"
            self.redirect(redirect_path)
        except Exception as inst:
            self.clear_all_cookies()
            render_error(self, traceback.format_exc())