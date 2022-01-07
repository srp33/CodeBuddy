import arrow
import base64
from fastapi import FastAPI, HTTPException
import getpass
import os
from pathlib import Path
from pydantic import BaseModel
import re
import json
import shutil
import subprocess
import tempfile
import traceback

class ExecInfo(BaseModel):
    image_name: str
    code: str
    tests: dict
    verification_code: str
    data_files: dict
    output_type: str
    memory_allowed_mb: int
    timeout_seconds: int

app = FastAPI()

@app.get("/hello")
def hello():
    return "world"

@app.post("/exec/")
def exec(info: ExecInfo):
    base_tmp_dir_path = f"/tmp/codebuddy_backend_{getpass.getuser()}"
    cpus = 1
    tmp_dir_path = None

    try:
        # This is meant to identify any old temp directories that inadvertently were not deleted.
        # This is not the best design, but it is simple.
        # It means we don't need to configure a separate process to run in the background.
        remove_old_temp_dirs(base_tmp_dir_path)

        os.makedirs(base_tmp_dir_path, exist_ok=True)
        tmp_dir_path = tempfile.mkdtemp(dir=base_tmp_dir_path)

        # Save the verification code to a file that will be accessible inside the container.
        if len(info.verification_code) > 0:
            with open(f"{tmp_dir_path}/verification_code", "w") as verification_file:
                verification_file.write(info.verification_code)

        # Save information for each test under a subdirectory under 'tests'.
        for test_title in info.tests:
            info.tests[test_title]["dir_path"] = f"{tmp_dir_path}/tests/{info.tests[test_title]['test_id']}"
            os.makedirs(info.tests[test_title]["dir_path"], exist_ok=True)

            if info.image_name.endswith("python_script"):
                info.tests[test_title]["code_file_name"] = "code.py"
                info.tests[test_title]["code"] = info.tests[test_title]["before_code"] + "\n\n" + info.tests[test_title]["after_code"]
            else:
                info.tests[test_title]["code_file_name"] = "code"
                info.tests[test_title]["code"] = info.tests[test_title]["before_code"] + "\n\n" + info.code + "\n\n" + info.tests[test_title]["after_code"]

            with open(f"{info.tests[test_title]['dir_path']}/{info.tests[test_title]['code_file_name']}", "w") as test_file:
                test_file.write(info.tests[test_title]["code"])

            # Save any data files so they will be accessible inside the container.
            for key, value in info.data_files.items():
                with open(f"{info.tests[test_title]['dir_path']}/{key}", "w") as data_file:
                    data_file.write(value)

        # About --cap-drop: https://www.redhat.com/en/blog/secure-your-containers-one-weird-trick
        docker_command = f"timeout -s 9 {info.timeout_seconds}s docker run --rm --user $(id -u):$(id -g) --ulimit cpu={info.timeout_seconds} --cpus {cpus} --memory={info.memory_allowed_mb}m --cap-drop=ALL --log-driver=none --workdir /sandbox -v {tmp_dir_path}/:/sandbox/ {info.image_name}:latest {info.output_type}"

        result = subprocess.run(docker_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        docker_warning = "WARNING: Your kernel does not support swap limit capabilities or the cgroup is not mounted. Memory limited without swap."
        stdout = result.stdout.decode().replace(docker_warning, "").strip()

        # Check whether the command timed out.
        if result.returncode == 137 or stdout == "Killed":
            raise Exception(f"The time to execute your code exceeded the timeout ({info.timeout_seconds} seconds) or was unable to complete for some other reason.")

        test_outputs = {}

        for test_title in info.tests:
            text_output = ""
            text_output_file_path = f"{info.tests[test_title]['dir_path']}/text_output"

            if os.path.exists(text_output_file_path):
                with open(text_output_file_path) as output_file:
                    text_output = output_file.read().strip()
            else:
                text_output = "No text output was generated."

            image_output = ""
            if info.output_type == "jpg":
                image_output_file_path = f"{info.tests[test_title]['dir_path']}/text_output"

                if os.path.exists(image_output_file_path):
                    with open(image_output_file_path, "rb") as output_file:
                        image_output = encode_image_bytes(output_file.read())
            else:
                image_output = "No image output was generated."

            test_outputs[test_title] = {"text_output": text_output, "image_output": image_output}
    except Exception as inst:
        return {"message": traceback.format_exc(), "test_outputs": {}}
    finally:
        if tmp_dir_path:
            shutil.rmtree(tmp_dir_path, ignore_errors=True)

    return {"message": "", "test_outputs": test_outputs}

def encode_image_bytes(b):
    return str(base64.b64encode(b), "utf-8")

# From https://stackoverflow.com/questions/12485666/python-deleting-all-files-in-a-folder-older-than-x-days
def remove_old_temp_dirs(dir_path):
    criticalTime = arrow.now().shift(minutes=-5)

    for item in Path(dir_path).glob("*"):
        itemTime = arrow.get(item.stat().st_mtime)
        if itemTime < criticalTime:
            shutil.rmtree(item, ignore_errors=True)
