# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseOtherHandler import *
from datetime import datetime, timezone
import jwt
from jwt import PyJWKClient

def get_lti_claim_id(claim_value):
    if isinstance(claim_value, dict):
        return claim_value.get("id")
    return claim_value

class LtiLaunchHandler(BaseOtherHandler):
    async def post(self):
        try:
            state = self.get_body_argument("state")
            id_token = self.get_body_argument("id_token")

            state_row = self.content.consume_lti_launch_state(state)
            if not state_row:
                raise Exception("Invalid or expired LTI launch state.")

            expires_at = datetime.fromisoformat(state_row["expires_at"])
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) > expires_at:
                raise Exception("LTI launch state has expired.")

            registration = self.content.get_lti_registration_by_id(state_row["registration_id"])
            if not registration:
                raise Exception("LTI registration could not be found for launch state.")

            jwk_client = PyJWKClient(registration["key_set_url"])
            signing_key = jwk_client.get_signing_key_from_jwt(id_token)
            launch_claims = jwt.decode(
                id_token,
                signing_key.key,
                algorithms=["RS256", "RS384", "RS512", "ES256", "ES384", "ES512"],
                audience=registration["client_id"],
                issuer=registration["issuer"],
                options={
                    "require": ["iss", "aud", "exp", "nonce"]
                }
            )

            if launch_claims.get("nonce") != state_row["nonce"]:
                raise Exception("LTI nonce does not match the login state.")

            target_link_uri_claim = "https://purl.imsglobal.org/spec/lti/claim/target_link_uri"
            launch_target_link_uri = launch_claims.get(target_link_uri_claim)
            if not launch_target_link_uri:
                raise Exception("LTI target_link_uri claim is missing.")
            if launch_target_link_uri != state_row["target_link_uri"]:
                raise Exception("LTI target_link_uri does not match the login initiation request.")

            deployment_id_claim = "https://purl.imsglobal.org/spec/lti/claim/deployment_id"
            deployment_id = launch_claims.get(deployment_id_claim)
            if not deployment_id:
                raise Exception("LTI deployment claim is missing.")

            if not self.content.lti_deployment_exists(registration["registration_id"], deployment_id):
                raise Exception("Unknown LTI deployment for this registration.")

            lti_sub = launch_claims.get("sub")
            if not lti_sub:
                raise Exception("LTI subject (sub) claim is missing.")

            user_id = self.content.get_lti_user_link(deployment_id, lti_sub)
            if not user_id:
                # First launch for this user/deployment: create local user with sub as user_id.
                user_id = str(lti_sub).strip()

            user_name = launch_claims.get("name", user_id)
            given_name = launch_claims.get("given_name", user_id)
            family_name = launch_claims.get("family_name", "")
            email_address = launch_claims.get("email", f"{user_id}@nospam.edu")
            locale = launch_claims.get("locale", "en")

            user_dict = {
                "name": user_name,
                "given_name": given_name,
                "family_name": family_name,
                "locale": locale,
                "email_address": email_address
            }

            if self.content.user_exists(user_id):
                self.content.update_user(user_id, user_dict)
            else:
                self.content.add_user(user_id, user_dict)

            self.content.upsert_lti_user_link(deployment_id, lti_sub, user_id)

            self.set_secure_cookie("user_id", user_id, expires_days=30)

            context_claim = "https://purl.imsglobal.org/spec/lti/claim/context"
            resource_link_claim = "https://purl.imsglobal.org/spec/lti/claim/resource_link"
            context_id = get_lti_claim_id(launch_claims.get(context_claim))
            resource_link_id = get_lti_claim_id(launch_claims.get(resource_link_claim))

            redirect_path = "/"
            if context_id and resource_link_id:
                mapping = self.content.get_lti_resource_link(deployment_id, context_id, resource_link_id)
                if mapping and mapping["course_id"] and mapping["assignment_id"]:
                    redirect_path = f"/assignment/{mapping['course_id']}/{mapping['assignment_id']}"

                    ags_endpoint_claim = "https://purl.imsglobal.org/spec/lti-ags/claim/endpoint"
                    ags_endpoint = launch_claims.get(ags_endpoint_claim)
                    lineitem_url = None
                    if isinstance(ags_endpoint, dict):
                        lineitem_url = ags_endpoint.get("lineitem")

                    self.content.upsert_lti_resource_link(
                        deployment_id,
                        context_id,
                        resource_link_id,
                        mapping["course_id"],
                        mapping["assignment_id"],
                        lineitem_url
                    )

            self.redirect(redirect_path)
        except Exception as inst:
            user_id_cookie = self.get_secure_cookie("user_id")
            if user_id_cookie:
                self.clear_cookie("user_id")

            render_error(self, traceback.format_exc())
