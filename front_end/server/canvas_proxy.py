# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

import json
import re
import time
from urllib.parse import urlencode, urlparse, urlunparse

import requests

CANVAS_CREDS_COOKIE = "codebuddy_canvas_creds"
CANVAS_CREDS_EXPIRES_DAYS = 30


def canvas_allowed_hosts(settings_dict):
    canvas = (settings_dict or {}).get("canvas") or {}
    hosts = canvas.get("allowed_hosts")
    if isinstance(hosts, list) and hosts:
        return [str(h).strip() for h in hosts if str(h).strip()]
    return ["*.instructure.com"]


def canvas_host_allowed(host, settings_dict):
    host = (host or "").lower().strip()
    if not host:
        return False
    for pattern in canvas_allowed_hosts(settings_dict):
        pattern = (pattern or "").lower().strip()
        if not pattern:
            continue
        if pattern.startswith("*."):
            suffix = pattern[1:]
            base = pattern[2:]
            if host == base or host.endswith(suffix):
                return True
        elif host == pattern:
            return True
    return False


def normalize_canvas_base_url(raw, settings_dict):
    text = (raw or "").strip()
    if not text:
        return None, "Canvas base URL is required"
    if "://" not in text:
        text = "https://" + text
    parsed = urlparse(text)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None, "Enter a valid Canvas base URL (e.g. https://canvas.example.edu)"
    host = (parsed.hostname or "").lower()
    if not canvas_host_allowed(host, settings_dict):
        allowed = ", ".join(canvas_allowed_hosts(settings_dict))
        return None, (
            f"Canvas host '{host}' is not allowed. "
            f"Allowed patterns: {allowed}"
        )
    return urlunparse((parsed.scheme, parsed.netloc, "", "", "", "")), None


def _normalize_codebuddy_course_id(raw):
    text = str(raw or "").strip()
    return text or None


def _read_all_canvas_course_creds(handler):
    raw = handler.get_secure_cookie(CANVAS_CREDS_COOKIE)
    if not raw:
        return {}
    try:
        data = json.loads(raw.decode("utf-8"))
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    courses = data.get("courses")
    if isinstance(courses, dict):
        return courses
    return {}


def read_canvas_creds_cookie(handler, codebuddy_course_id):
    key = _normalize_codebuddy_course_id(codebuddy_course_id)
    if not key:
        return None
    entry = _read_all_canvas_course_creds(handler).get(key)
    if not isinstance(entry, dict):
        return None
    base_url = (entry.get("base_url") or "").strip()
    course_id = str(entry.get("course_id") or "").strip()
    token = (entry.get("access_token") or "").strip()
    if not base_url or not course_id or not token:
        return None
    return {
        "base_url": base_url,
        "course_id": course_id,
        "access_token": token,
    }


def apply_canvas_creds_cookie(handler, codebuddy_course_id, base_url, course_id, token):
    key = _normalize_codebuddy_course_id(codebuddy_course_id)
    if not key:
        return
    courses = _read_all_canvas_course_creds(handler)
    courses[key] = {
        "base_url": base_url,
        "course_id": course_id,
        "access_token": token,
    }
    payload = json.dumps({"courses": courses})
    handler.set_secure_cookie(
        CANVAS_CREDS_COOKIE,
        payload,
        expires_days=CANVAS_CREDS_EXPIRES_DAYS,
        httponly=True,
        samesite="Lax",
    )


def clear_canvas_creds_cookie(handler, codebuddy_course_id=None):
    key = _normalize_codebuddy_course_id(codebuddy_course_id)
    if not key:
        handler.clear_cookie(CANVAS_CREDS_COOKIE)
        return
    courses = _read_all_canvas_course_creds(handler)
    if key not in courses:
        return
    courses.pop(key, None)
    if not courses:
        handler.clear_cookie(CANVAS_CREDS_COOKIE)
        return
    payload = json.dumps({"courses": courses})
    handler.set_secure_cookie(
        CANVAS_CREDS_COOKIE,
        payload,
        expires_days=CANVAS_CREDS_EXPIRES_DAYS,
        httponly=True,
        samesite="Lax",
    )


def parse_canvas_credentials(handler, data):
    codebuddy_course_id = str((data or {}).get("codebuddy_course_id") or "").strip()
    saved = read_canvas_creds_cookie(handler, codebuddy_course_id) or {}
    raw_base = (data or {}).get("base_url")
    if raw_base is None or str(raw_base).strip() == "":
        raw_base = saved.get("base_url")
    base_url, err = normalize_canvas_base_url(raw_base, handler.settings_dict)
    if err:
        return None, None, None, err, 400

    course_id = str((data or {}).get("course_id") or "").strip()
    if not course_id:
        course_id = str(saved.get("course_id") or "").strip()
    if not course_id or not re.fullmatch(r"\d+", course_id):
        return None, None, None, "Course ID must be a numeric Canvas course id", 400

    token = ((data or {}).get("access_token") or "").strip()
    if not token:
        token = (saved.get("access_token") or "").strip()
    if not token:
        return None, None, None, "Access token is required", 400
    return base_url, course_id, token, None, 200


def canvas_get_paginated(url, headers, *, max_pages=50):
    items = []
    next_url = url
    for _ in range(max_pages):
        try:
            resp = requests.get(next_url, headers=headers, timeout=30)
        except requests.RequestException as exc:
            return None, f"Could not reach Canvas: {exc}", 502
        if resp.status_code == 401:
            return None, "Canvas rejected the access token (unauthorized)", 401
        if resp.status_code == 403:
            return None, "Canvas denied access to this resource (forbidden)", 403
        if resp.status_code == 404:
            return None, "Canvas course or resource not found", 404
        if not resp.ok:
            detail = (resp.text or "").strip()[:240]
            return None, (
                f"Canvas returned HTTP {resp.status_code}"
                + (f": {detail}" if detail else "")
            ), 502
        try:
            payload = resp.json()
        except ValueError:
            return None, "Canvas returned a non-JSON response", 502
        if not isinstance(payload, list):
            return None, "Unexpected Canvas response shape", 502
        items.extend(payload)
        next_url = resp.links.get("next", {}).get("url")
        if not next_url:
            break
    return items, None, 200


def canvas_login_id(raw):
    login = str(raw or "").strip()
    if "@" in login:
        login = login.split("@", 1)[0].strip()
    return login


def write_json(handler, payload, status=200, *, clear_cookie=False, save_creds=None, codebuddy_course_id=None):
    handler.set_status(status)
    handler.set_header("Content-Type", "application/json; charset=UTF-8")
    cb_id = codebuddy_course_id
    if save_creds and save_creds.get("codebuddy_course_id"):
        cb_id = save_creds.get("codebuddy_course_id")
    if clear_cookie:
        clear_canvas_creds_cookie(handler, cb_id)
    elif save_creds:
        apply_canvas_creds_cookie(
            handler,
            cb_id,
            save_creds["base_url"],
            save_creds["course_id"],
            save_creds["access_token"],
        )
    handler.write(json.dumps(payload))


def post_canvas_grades(base_url, course_id, token, assignment_id, grades):
    form = {}
    uploaded = 0
    for row in grades:
        if not isinstance(row, dict):
            continue
        uid = str(row.get("canvas_user_id") or "").strip()
        if not uid or not re.fullmatch(r"\d+", uid):
            continue
        try:
            score = float(row.get("score"))
        except (TypeError, ValueError):
            return None, f"Invalid score for Canvas user {uid}", 400
        if score < 0 or score > 100:
            return None, f"Score for Canvas user {uid} must be between 0 and 100", 400
        form[f"grade_data[{uid}][posted_grade]"] = f"{score:g}%"
        uploaded += 1

    if not uploaded:
        return None, "No valid grades to upload", 400

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    url = (
        f"{base_url}/api/v1/courses/{course_id}/assignments/{assignment_id}"
        "/submissions/update_grades"
    )
    try:
        resp = requests.post(url, headers=headers, data=form, timeout=60)
    except requests.RequestException as exc:
        return None, f"Could not reach Canvas: {exc}", 502

    if resp.status_code == 401:
        return None, "Canvas rejected the access token (unauthorized)", 401
    if resp.status_code == 403:
        return None, "Canvas denied access to update grades (forbidden)", 403
    if resp.status_code == 404:
        return None, "Canvas course or assignment not found", 404
    if not resp.ok:
        detail = (resp.text or "").strip()[:240]
        return None, (
            f"Canvas returned HTTP {resp.status_code}"
            + (f": {detail}" if detail else "")
        ), 502

    progress = None
    try:
        progress = resp.json()
    except ValueError:
        progress = None

    progress_id = progress.get("id") if isinstance(progress, dict) else None
    workflow = (progress or {}).get("workflow_state") if isinstance(progress, dict) else None
    if progress_id and workflow not in ("completed", "failed"):
        prog_url = f"{base_url}/api/v1/progress/{progress_id}"
        for _ in range(20):
            try:
                prog_resp = requests.get(prog_url, headers=headers, timeout=30)
            except requests.RequestException:
                break
            if not prog_resp.ok:
                break
            try:
                progress = prog_resp.json()
            except ValueError:
                break
            workflow = progress.get("workflow_state")
            if workflow in ("completed", "failed"):
                break
            time.sleep(0.5)

    if isinstance(progress, dict) and progress.get("workflow_state") == "failed":
        msg = progress.get("message") or "Canvas grade upload failed"
        return None, msg, 502

    return {
        "uploaded": uploaded,
        "progress": progress if isinstance(progress, dict) else None,
    }, None, 200


def fetch_canvas_submissions(base_url, course_id, token, assignment_ids):
    ids = []
    seen = set()
    for raw in assignment_ids or []:
        aid = str(raw or "").strip()
        if not aid or not re.fullmatch(r"\d+", aid) or aid in seen:
            continue
        seen.add(aid)
        ids.append(aid)

    if not ids:
        return {"scores": {}}, None, 200

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    params = [("per_page", "100"), ("student_ids[]", "all")]
    for aid in ids:
        params.append(("assignment_ids[]", aid))
    url = (
        f"{base_url}/api/v1/courses/{course_id}/students/submissions"
        f"?{urlencode(params)}"
    )
    rows, err, status = canvas_get_paginated(url, headers, max_pages=100)
    if err:
        return None, err, status

    scores = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        aid = str(row.get("assignment_id") or "").strip()
        uid = str(row.get("user_id") or "").strip()
        if not aid or not uid:
            continue
        if aid not in scores:
            scores[aid] = {}
        scores[aid][uid] = {
            "score": row.get("score"),
            "grade": row.get("grade"),
        }

    return {"scores": scores}, None, 200
