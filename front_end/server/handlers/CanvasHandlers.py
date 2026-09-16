# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *
from canvas_proxy import *


class CanvasHandlersMixin:
    async def require_canvas_course_access(self, course_id):
        """Only administrators and course instructors may push grades to Canvas (not assistants)."""
        if not course_id:
            write_json(self, {"error": "A CodeBuddy course id is required."}, 400)
            return False
        if self.is_administrator:
            return True
        if await self.is_instructor_for_course(course_id):
            return True
        # Assistants and students are intentionally denied.
        write_json(self, {"error": "Permission denied"}, 403)
        return False

    def request_json(self):
        return ujson.loads(self.request.body) if self.request.body else {}


class CanvasSavedCredentialsHandler(BaseUserHandler, CanvasHandlersMixin):
    async def get(self):
        try:
            course_id = self.get_argument("codebuddy_course_id", None)
            if not await self.require_canvas_course_access(course_id):
                return

            saved = read_canvas_creds_cookie(self)
            if not saved:
                return write_json(self, {
                    "base_url": "",
                    "course_id": "",
                    "has_token": False,
                })
            return write_json(self, {
                "base_url": saved["base_url"],
                "course_id": saved["course_id"],
                "has_token": True,
            })
        except Exception:
            return write_json(self, {"error": traceback.format_exc()}, 500)

    async def delete(self):
        try:
            course_id = self.get_argument("codebuddy_course_id", None)
            if not await self.require_canvas_course_access(course_id):
                return
            clear_canvas_creds_cookie(self)
            return write_json(self, {"message": "Saved Canvas credentials cleared"})
        except Exception:
            return write_json(self, {"error": traceback.format_exc()}, 500)


class CanvasAssignmentsHandler(BaseUserHandler, CanvasHandlersMixin):
    async def post(self):
        try:
            data = self.request_json()
            course_id = str(data.get("codebuddy_course_id") or "").strip()
            if not await self.require_canvas_course_access(course_id):
                return

            base_url, canvas_course_id, token, err, status = parse_canvas_credentials(self, data)
            if err:
                return write_json(self, {"error": err}, status)

            headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
            url = (
                f"{base_url}/api/v1/courses/{canvas_course_id}/assignments"
                f"?per_page=100&order_by=due_at&include[]=all_dates"
            )
            rows, err, status = canvas_get_paginated(url, headers)
            if err:
                return write_json(self, {"error": err}, status, clear_cookie=(status == 401))

            assignments = []
            for row in rows:
                if not isinstance(row, dict):
                    continue
                assignments.append({
                    "id": row.get("id"),
                    "name": row.get("name") or "",
                    "due_at": row.get("due_at"),
                    "points_possible": row.get("points_possible"),
                    "published": bool(row.get("published")),
                    "html_url": row.get("html_url") or "",
                })

            return write_json(self, {
                "base_url": base_url,
                "course_id": canvas_course_id,
                "assignments": assignments,
                "saved": True,
            }, save_creds={
                "base_url": base_url,
                "course_id": canvas_course_id,
                "access_token": token,
            })
        except Exception:
            return write_json(self, {"error": traceback.format_exc()}, 500)


class CanvasStudentsHandler(BaseUserHandler, CanvasHandlersMixin):
    async def post(self):
        try:
            data = self.request_json()
            course_id = str(data.get("codebuddy_course_id") or "").strip()
            if not await self.require_canvas_course_access(course_id):
                return

            base_url, canvas_course_id, token, err, status = parse_canvas_credentials(self, data)
            if err:
                return write_json(self, {"error": err}, status)

            headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
            url = (
                f"{base_url}/api/v1/courses/{canvas_course_id}/users"
                f"?per_page=100&enrollment_type[]=student&include[]=email"
            )
            rows, err, status = canvas_get_paginated(url, headers)
            if err:
                return write_json(self, {"error": err}, status, clear_cookie=(status == 401))

            students = []
            for row in rows:
                if not isinstance(row, dict):
                    continue
                students.append({
                    "id": row.get("id"),
                    "name": row.get("name") or "",
                    "sortable_name": row.get("sortable_name") or row.get("name") or "",
                    "login_id": canvas_login_id(row.get("login_id")),
                    "email": row.get("email") or "",
                    "sis_user_id": row.get("sis_user_id") or "",
                    "integration_id": row.get("integration_id") or "",
                })

            return write_json(self, {
                "base_url": base_url,
                "course_id": canvas_course_id,
                "students": students,
                "saved": True,
            }, save_creds={
                "base_url": base_url,
                "course_id": canvas_course_id,
                "access_token": token,
            })
        except Exception:
            return write_json(self, {"error": traceback.format_exc()}, 500)


class CanvasGradesHandler(BaseUserHandler, CanvasHandlersMixin):
    async def post(self):
        try:
            data = self.request_json()
            course_id = str(data.get("codebuddy_course_id") or "").strip()
            if not await self.require_canvas_course_access(course_id):
                return

            base_url, canvas_course_id, token, err, status = parse_canvas_credentials(self, data)
            if err:
                return write_json(self, {"error": err}, status)

            assignment_id = str(data.get("assignment_id") or "").strip()
            if not assignment_id or not re.fullmatch(r"\d+", assignment_id):
                return write_json(self, {"error": "Assignment ID must be a numeric Canvas assignment id"}, 400)

            grades = data.get("grades")
            if not isinstance(grades, list) or not grades:
                return write_json(self, {"error": "At least one grade is required"}, 400)

            result, err, status = post_canvas_grades(base_url, canvas_course_id, token, assignment_id, grades)
            if err:
                return write_json(self, {"error": err}, status, clear_cookie=(status == 401))

            return write_json(self, {
                "base_url": base_url,
                "course_id": canvas_course_id,
                "assignment_id": assignment_id,
                "uploaded": result["uploaded"],
                "progress": result.get("progress"),
                "saved": True,
            }, save_creds={
                "base_url": base_url,
                "course_id": canvas_course_id,
                "access_token": token,
            })
        except Exception:
            return write_json(self, {"error": traceback.format_exc()}, 500)


class CanvasSubmissionsHandler(BaseUserHandler, CanvasHandlersMixin):
    async def post(self):
        try:
            data = self.request_json()
            course_id = str(data.get("codebuddy_course_id") or "").strip()
            if not await self.require_canvas_course_access(course_id):
                return

            base_url, canvas_course_id, token, err, status = parse_canvas_credentials(self, data)
            if err:
                return write_json(self, {"error": err}, status)

            assignment_ids = data.get("assignment_ids")
            if assignment_ids is None:
                assignment_ids = []
            if not isinstance(assignment_ids, list):
                assignment_ids = [assignment_ids]

            result, err, status = fetch_canvas_submissions(
                base_url, canvas_course_id, token, assignment_ids
            )
            if err:
                return write_json(self, {"error": err}, status, clear_cookie=(status == 401))

            return write_json(self, {
                "base_url": base_url,
                "course_id": canvas_course_id,
                "scores": result.get("scores") or {},
                "saved": True,
            }, save_creds={
                "base_url": base_url,
                "course_id": canvas_course_id,
                "access_token": token,
            })
        except Exception:
            return write_json(self, {"error": traceback.format_exc()}, 500)


class CanvasCourseGradebookHandler(BaseUserHandler, CanvasHandlersMixin):
    async def get(self, course_id):
        try:
            if not await self.require_canvas_course_access(course_id):
                return

            course_basics = await self.get_course_basics(course_id)
            if not course_basics["exists"]:
                return write_json(self, {"error": "This course does not exist."}, 404)

            gradebook = self.content.get_course_gradebook_for_canvas(course_basics)
            return write_json(self, gradebook)
        except Exception:
            return write_json(self, {"error": traceback.format_exc()}, 500)
