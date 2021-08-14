from tornado.web import *
from tornado.auth import GoogleOAuth2Mixin
from cas import CASClient
from content import *

# See https://djangocas.dev/blog/python-cas-flask-example/
class CASLoginHandler(RequestHandler, GoogleOAuth2Mixin):
    def prepare(self):
        self.settings_dict = load_yaml_dict(read_file("/Settings.yaml"))
        self.content = Content(self.settings_dict)

    async def get(self):
        try:
            #TODO: Change webserver.py to point to /login
            #TODO: Update logout logic?
            #TODO: NetID is showing up as email address.
            #TODO: Remove locale from Personal Info page.
            #TODO: Put server_url in settings? Not sure because not sure if attributes coming back from CAS are standardized.
            #TODO: Figure out how to migrate users from old accounts to CAS? Or just give them multiple login options?
            #TODO: Change the service_url (see below).
            service_url="http://lscodebuddy.byu.edu:8008/login?next=%2Flogin"
            #service_url = f"https://{self.settings_dict['domain']}/login?next=%2Flogin"
            server_url="https://cas.byu.edu/cas/"

            cas_client = CASClient(version=3, service_url=service_url, server_url=server_url)

            ticket = self.get_argument('ticket', False)
            if not ticket:
                cas_login_url = cas_client.get_login_url()
                self.redirect(cas_login_url)

            user_id, attributes, pgtiou = cas_client.verify_ticket(ticket)
            user_dict = {"name": attributes["preferredFirstName"] + " " + attributes["preferredSurname"], "given_name": attributes["preferredFirstName"], "family_name": attributes["preferredSurname"], "locale": "en"}

            #nxt = self.get_argument('next', False)

            if self.content.user_exists(user_id):
                # Update user with current information when they already exist.
                self.content.update_user(user_id, user_dict)
            else:
                # Store current user information when they do not already exist.
                self.content.add_user(user_id, user_dict)

            self.set_secure_cookie("user_id", user_id, expires_days=30)

            # TODO: Make sure this works.
            redirect_path = self.get_secure_cookie("redirect_path")
            self.clear_cookie("redirect_path")
            if not redirect_path:
                redirect_path = "/"
            self.redirect(redirect_path)
        except Exception as inst:
            self.clear_all_cookies()
            render_error(self, traceback.format_exc())
