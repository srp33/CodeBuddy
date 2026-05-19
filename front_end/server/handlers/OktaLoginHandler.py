# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

import hashlib
import os
import secrets
import tempfile
import time
import urllib.parse

from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.web import *
# https://www.tornadoweb.org/en/latest/auth.html

from content import *

# How long to reuse the downloaded Okta "where to log in" file before fetching again.
_DISCOVERY_CACHE_MAX_AGE_SEC = 24 * 60 * 60


class OktaLoginHandler(RequestHandler):
    def prepare(self):
        # Site-wide options (domain name, ports, etc.).
        self.settings_dict = load_yaml_dict(read_file("../Settings.yaml"))
        # Database layer for saving who logged in.
        self.content = Content(self.settings_dict)

    async def _fetch_discovery(self, issuer):
        # Ask Okta where login-related web addresses live for this account.
        discovery_url = f"{issuer}/.well-known/openid-configuration"
        # Pick a safe file name so each Okta "issuer" keeps its own saved copy.
        issuer_key = hashlib.sha256(discovery_url.encode("utf-8")).hexdigest()[:24]
        cache_path = os.path.join(
            tempfile.gettempdir(),
            f"codebuddy_okta_oidc_discovery_{issuer_key}.json",
        )

        now = time.time()
        if os.path.isfile(cache_path):
            try:
                # Use our saved copy if it is less than a day old.
                if now - os.path.getmtime(cache_path) < _DISCOVERY_CACHE_MAX_AGE_SEC:
                    with open(cache_path, encoding="utf-8") as cache_file:
                        return ujson.loads(cache_file.read())
            except (OSError, ValueError):
                # Saved copy missing or bad — fall through and download again.
                pass

        # Download the latest copy from Okta.
        client = AsyncHTTPClient()
        resp = await client.fetch(discovery_url, method="GET", raise_error=False)
        if resp.code != 200:
            return None
        data = ujson.loads(resp.body.decode("utf-8"))

        # Write to a side file first, then swap it in, so we never leave a half-finished file.
        tmp_path = cache_path + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as tmp_file:
                tmp_file.write(ujson.dumps(data))
            os.replace(tmp_path, cache_path)
        except OSError:
            try:
                if os.path.isfile(tmp_path):
                    os.unlink(tmp_path)
            except OSError:
                pass
        return data

    async def _post_form(self, url, body):
        # Send a normal HTML form-style POST (how Okta expects the token step).
        client = AsyncHTTPClient()
        req = HTTPRequest(
            url,
            method="POST",
            body=body.encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        return await client.fetch(req, raise_error=False)

    async def _get_userinfo(self, url, access_token):
        # Ask Okta for this person's name and email using the short-lived access token.
        client = AsyncHTTPClient()
        req = HTTPRequest(
            url,
            method="GET",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        return await client.fetch(req, raise_error=False)

    async def get(self):
        try:
            print("OktaLoginHandler.get()")
            self.write("OktaLoginHandler.get()")
            self.finish()
            # return

            # Secrets from the server config (not checked into git).
            cfg = self.settings.get("okta_oauth") or {}
            issuer = (cfg.get("issuer") or "").rstrip("/")
            client_id = cfg.get("client_id") or ""
            client_secret = cfg.get("client_secret") or ""
            if not issuer or not client_id or not client_secret:
                render_error(self, "Okta OAuth is not configured.")
                return

            # Must match exactly what you registered in the Okta admin console.
            redirect_uri = f"https://{self.settings_dict['domain']}/oktalogin"

            discovery = await self._fetch_discovery(issuer)
            if not discovery:
                render_error(self, "Could not load Okta OpenID configuration.")
                return

            # Okta sends the user back here with an error message instead of a code.
            if self.get_argument("error", False):
                desc = self.get_argument("error_description", "")
                err = self.get_argument("error", "")
                render_error(self, f"Okta authentication error: {err} {desc}".strip())
                return

            # After login, Okta redirects here with a one-time "code" in the URL.
            code = self.get_argument("code", False)
            if code:
                # Make sure this callback matches the login we started (guards against forged requests).
                cookie_state = self.get_secure_cookie("okta_oauth_state")
                self.clear_cookie("okta_oauth_state")
                if (
                    not cookie_state
                    or cookie_state.decode("utf-8") != self.get_argument("state", "")
                ):
                    render_error(self, "Okta authentication failed: invalid OAuth state.")
                    return

                # Trade the code for tokens Okta can use to prove who this user is.
                token_body = urllib.parse.urlencode(
                    {
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": redirect_uri,
                        "client_id": client_id,
                        "client_secret": client_secret,
                    }
                )
                token_resp = await self._post_form(discovery["token_endpoint"], token_body)
                if token_resp.code != 200:
                    render_error(self, "Okta token exchange failed.")
                    return

                tokens = ujson.loads(token_resp.body.decode("utf-8"))
                access_token = tokens.get("access_token")
                if not access_token:
                    render_error(self, "Okta did not return an access token.")
                    return

                # Fetch profile details (name, email, etc.).
                userinfo_resp = await self._get_userinfo(
                    discovery["userinfo_endpoint"], access_token
                )
                if userinfo_resp.code != 200:
                    # Avoid leaving an old login active if this step fails.
                    user_id_cookie = self.get_secure_cookie("user_id")
                    if user_id_cookie:
                        self.clear_cookie("user_id")
                    render_error(self, "Okta account information could not be retrieved.")
                    return

                claims = ujson.loads(userinfo_resp.body.decode("utf-8"))
                # Prefer a real email; some setups only expose a username-style value.
                email = claims.get("email") or claims.get("preferred_username") or ""
                if "@" not in email:
                    render_error(
                        self,
                        "Okta did not return an email address; cannot create a user ID.",
                    )
                    return

                # Same idea as Google login: use the part before @ as the CodeBuddy user id.
                user_id = email.split("@")[0]
                user_dict = {
                    "name": claims.get("name") or "",
                    "given_name": claims.get("given_name") or "",
                    "family_name": claims.get("family_name") or "",
                    "locale": claims.get("locale") or "en",
                    "email_address": email,
                }

                # Create the row on first visit; refresh name/email on later visits.
                if self.content.user_exists(user_id):
                    self.content.update_user(user_id, user_dict)
                else:
                    self.content.add_user(user_id, user_dict)

                # Remember them in the browser for the next few weeks.
                self.set_secure_cookie("user_id", user_id, expires_days=30)

                # Send them back to whatever page they tried to open before logging in.
                redirect_path = self.get_secure_cookie("redirect_path")
                self.clear_cookie("redirect_path")
                if not redirect_path:
                    redirect_path = "/"
                self.redirect(redirect_path)
                return

            # First visit: no code yet — send the browser to Okta to sign in.
            state = secrets.token_urlsafe(32)
            self.set_secure_cookie("okta_oauth_state", state, expires_days=1)

            auth_params = urllib.parse.urlencode(
                {
                    "client_id": client_id,
                    "redirect_uri": redirect_uri,
                    "response_type": "code",
                    "scope": "openid profile email",
                    "state": state,
                }
            )
            authorize_url = f"{discovery['authorization_endpoint']}?{auth_params}"
            self.redirect(authorize_url)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def finish(self, chunk=None):
        # Close the database handle opened in prepare().
        self.content.close()
        super().finish(chunk)
