# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseOtherHandler import *
from urllib.parse import urlencode
import secrets
from datetime import datetime, timedelta, timezone

class LtiLoginHandler(BaseOtherHandler):
    def get_base_url(self):
        if self.in_production_mode():
            return f"https://{self.settings_dict['domain']}"
        return f"http://localhost:{self.settings_dict['f_port']}"

    async def get(self):
        try:
            issuer = self.get_argument("iss")
            client_id = self.get_argument("client_id")
            target_link_uri = self.get_argument("target_link_uri")
            login_hint = self.get_argument("login_hint")
            lti_message_hint = self.get_argument("lti_message_hint", default=None)

            registration = self.content.get_lti_registration(issuer, client_id)
            if not registration:
                raise Exception("Unknown LTI registration for issuer/client_id.")

            state = secrets.token_urlsafe(32)
            nonce = secrets.token_urlsafe(32)
            expires_at = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
            self.content.create_lti_launch_state(state, nonce, registration["registration_id"], target_link_uri, expires_at)

            params = {
                "scope": "openid",
                "response_type": "id_token",
                "response_mode": "form_post",
                "prompt": "none",
                "client_id": client_id,
                "redirect_uri": f"{self.get_base_url()}/lti/launch",
                "login_hint": login_hint,
                "state": state,
                "nonce": nonce
            }
            if lti_message_hint:
                params["lti_message_hint"] = lti_message_hint

            self.redirect(registration["auth_login_url"] + "?" + urlencode(params))
        except Exception as inst:
            render_error(self, traceback.format_exc())
