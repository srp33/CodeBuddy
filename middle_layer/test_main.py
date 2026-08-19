# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

import os
import unittest
from unittest.mock import MagicMock, patch

from main import ExecInfo, build_docker_command, validate_exec_params


def make_info(**overrides):
    data = {
        "image_name": "codebuddy/python_development",
        "code": "print(1)",
        "tests": {},
        "verification_code": "",
        "data_files": {},
        "output_type": "txt",
        "memory_allowed_mb": 500,
        "timeout_seconds": 60,
    }
    data.update(overrides)
    return ExecInfo(**data)


class ValidateExecParamsTests(unittest.TestCase):
    def test_accepts_valid_params(self):
        validate_exec_params(make_info())

    def test_rejects_shell_metacharacters_in_image_name(self):
        with self.assertRaises(ValueError):
            validate_exec_params(make_info(image_name="codebuddy/python_development; touch /tmp/pwned"))

    def test_rejects_command_substitution_in_image_name(self):
        with self.assertRaises(ValueError):
            validate_exec_params(make_info(image_name="codebuddy/$(id)_development"))

    def test_rejects_invalid_output_type(self):
        with self.assertRaises(ValueError):
            validate_exec_params(make_info(output_type="txt; rm -rf /"))

    def test_rejects_unknown_output_type(self):
        with self.assertRaises(ValueError):
            validate_exec_params(make_info(output_type="pdf"))

    def test_rejects_non_positive_memory(self):
        with self.assertRaises(ValueError):
            validate_exec_params(make_info(memory_allowed_mb=0))


class BuildDockerCommandTests(unittest.TestCase):
    def test_development_command_is_argv_list_without_shell(self):
        info = make_info(timeout_seconds=-1)
        cmd = build_docker_command(info, "/tmp/codebuddy_backend/xyz", False, 1)

        self.assertIsInstance(cmd, list)
        self.assertEqual(cmd[0], "docker")
        self.assertIn("codebuddy/python_development:latest", cmd)
        self.assertEqual(cmd[-2:], ["False", "txt"])
        # Metacharacters in path would be a single argv element, not interpreted by a shell.
        self.assertIn("/tmp/codebuddy_backend/xyz:/sandbox", cmd)

    def test_production_command_resolves_user_without_shell(self):
        info = make_info(timeout_seconds=30, memory_allowed_mb=256)
        cmd = build_docker_command(info, "/tmp/codebuddy_backend/xyz", True, 1)

        self.assertEqual(cmd[0], "timeout")
        self.assertEqual(cmd[1:4], ["-s", "9", "30s"])
        self.assertIn("docker", cmd)
        self.assertEqual(cmd[cmd.index("--user") + 1], f"{os.getuid()}:{os.getgid()}")
        self.assertIn("--memory=256m", cmd)
        self.assertEqual(cmd[-2:], ["True", "txt"])

    def test_injection_payload_stays_single_argv_element(self):
        # Even if validation were bypassed, shell=False keeps this one argument.
        info = make_info(image_name="codebuddy/python_development", output_type="txt")
        cmd = build_docker_command(info, "/tmp/x", False, 1)
        joined = " ".join(cmd)
        self.assertNotIn("shell=True", joined)
        self.assertTrue(all(isinstance(part, str) for part in cmd))


class ExecEndpointTests(unittest.TestCase):
    @patch("main.subprocess.run")
    @patch("main.tempfile.mkdtemp", return_value="/tmp/codebuddy_backend/testdir")
    @patch("main.remove_old_temp_dirs")
    @patch("main.shutil.rmtree")
    @patch("main.os.makedirs")
    def test_exec_uses_shell_false(self, _makedirs, _rmtree, _remove_old, _mkdtemp, mock_run):
        from fastapi.testclient import TestClient
        from main import app

        mock_run.return_value = MagicMock(returncode=0, stdout=b"")

        client = TestClient(app)
        response = client.post("/exec/", json={
            "image_name": "codebuddy/python_development",
            "code": "print(1)",
            "tests": {},
            "verification_code": "",
            "data_files": {},
            "output_type": "txt",
            "memory_allowed_mb": 500,
            "timeout_seconds": -1,
        })

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertIsInstance(args[0], list)
        self.assertFalse(kwargs.get("shell", True))

    @patch("main.subprocess.run")
    def test_exec_rejects_malicious_image_name(self, mock_run):
        from fastapi.testclient import TestClient
        from main import app

        client = TestClient(app)
        response = client.post("/exec/", json={
            "image_name": "codebuddy/python_development; id",
            "code": "print(1)",
            "tests": {},
            "verification_code": "",
            "data_files": {},
            "output_type": "txt",
            "memory_allowed_mb": 500,
            "timeout_seconds": -1,
        })

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("Invalid image_name", body["message"])
        mock_run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
