# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class ManageLtiHandler(BaseUserHandler):
    def _render_page(self, message="", is_error=False):
        registrations = self.content.get_lti_registrations()
        resource_links = self.content.get_lti_resource_links()
        registration_list = []

        for registration in registrations:
            registration_dict = dict(registration)
            registration_dict["deployments"] = self.content.get_lti_deployments_by_registration(registration["registration_id"])
            registration_list.append(registration_dict)

        self.render("manage_lti.html", registrations=registration_list, resource_links=resource_links, message=message, is_error=is_error, user_info=self.user_info, is_administrator=self.is_administrator)

    async def get(self):
        try:
            if self.is_administrator:
                self._render_page()
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def post(self):
        try:
            if not self.is_administrator:
                self.render("permissions.html")
                return

            action = self.get_body_argument("action")

            if action == "add_registration":
                platform_name = self.get_body_argument("platform_name").strip()
                issuer = self.get_body_argument("issuer").strip()
                client_id = self.get_body_argument("client_id").strip()
                auth_login_url = self.get_body_argument("auth_login_url").strip()
                auth_token_url = self.get_body_argument("auth_token_url").strip()
                key_set_url = self.get_body_argument("key_set_url").strip()

                if "" in [platform_name, issuer, client_id, auth_login_url, auth_token_url, key_set_url]:
                    self._render_page("Error: All registration fields are required.", True)
                    return

                self.content.add_lti_registration(platform_name, issuer, client_id, auth_login_url, auth_token_url, key_set_url)
                self._render_page("Success! LTI registration was added.", False)
                return

            if action == "add_deployment":
                registration_id = self.get_body_argument("registration_id").strip()
                deployment_id = self.get_body_argument("deployment_id").strip()

                if "" in [registration_id, deployment_id]:
                    self._render_page("Error: Registration ID and deployment ID are required.", True)
                    return

                self.content.add_lti_deployment(int(registration_id), deployment_id)
                self._render_page("Success! LTI deployment was added.", False)
                return

            if action == "toggle_deployment":
                deployment_id = self.get_body_argument("deployment_id").strip()
                is_active = self.get_body_argument("is_active").strip()

                if deployment_id == "" or is_active not in ["0", "1"]:
                    self._render_page("Error: Invalid deployment toggle request.", True)
                    return

                self.content.set_lti_deployment_active(deployment_id, int(is_active))
                self._render_page("Success! Deployment status was updated.", False)
                return

            if action == "add_resource_link":
                deployment_id = self.get_body_argument("deployment_id").strip()
                context_id = self.get_body_argument("context_id").strip()
                resource_link_id = self.get_body_argument("resource_link_id").strip()
                course_id = self.get_body_argument("course_id").strip()
                assignment_id = self.get_body_argument("assignment_id").strip()
                lineitem_url = self.get_body_argument("lineitem_url", default="").strip()

                if "" in [deployment_id, context_id, resource_link_id, course_id, assignment_id]:
                    self._render_page("Error: Deployment, context, resource link, course, and assignment are required.", True)
                    return

                self.content.upsert_lti_resource_link(
                    deployment_id,
                    context_id,
                    resource_link_id,
                    int(course_id),
                    int(assignment_id),
                    lineitem_url if lineitem_url != "" else None
                )
                self._render_page("Success! LTI resource link mapping was saved.", False)
                return

            self._render_page("Error: Unsupported action.", True)
        except Exception as inst:
            self._render_page(f"Error: {traceback.format_exc()}", True)
