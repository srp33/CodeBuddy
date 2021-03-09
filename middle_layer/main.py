import arrow
import base64
from fastapi import FastAPI, HTTPException
import getpass
import os
from pathlib import Path
from pydantic import BaseModel
import re
import shutil
import subprocess
import tempfile
import traceback

class ExecInfo(BaseModel):
    image_name: str
    code: str
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

        # Save the user's code to a file that will be accessible inside the container.
        with open(f"{tmp_dir_path}/code", "w") as code_file:
            code_file.write(info.code)

        if info.data_files != "":
            for key, value in info.data_files.items():
                with open(f"{tmp_dir_path}/{key}", "w") as data_file:
                    data_file.write(value)

        # About --cap-drop: https://www.redhat.com/en/blog/secure-your-containers-one-weird-trick
        docker_command = f"timeout -s 9 {info.timeout_seconds}s docker run --rm --user $(id -u):$(id -g) --ulimit cpu={info.timeout_seconds} --cpus {cpus} --memory={info.memory_allowed_mb}m --cap-drop=ALL --log-driver=none --workdir /sandbox -v {tmp_dir_path}/:/sandbox/ {info.image_name}:latest /sandbox/code {info.output_type}"

        result = subprocess.run(docker_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        docker_warning = "WARNING: Your kernel does not support swap limit capabilities or the cgroup is not mounted. Memory limited without swap."
        stdout = result.stdout.decode().replace(docker_warning, "").strip()

        # Check whether the command timed out.
        if result.returncode == 137 or stdout == "Killed":
            return {"text_output": f"The time to execute your code exceeded {info.timeout_seconds} seconds.", "image_output": ""}

        text_output_lines = []
        image_output = ""

        for text_output_line in stdout.split("\n"):
            text_output_line = text_output_line.strip()
            if text_output_line == "" or text_output_line == docker_warning:
                continue
            text_output_lines.append(text_output_line)

        if info.output_type == "jpg":
            image_file_path = f"{tmp_dir_path}/image_output"

            if os.path.exists(image_file_path):
                with open(image_file_path, "rb") as output_file:
                    image_output = encode_image_bytes(output_file.read())

        return {"text_output": "\n".join(text_output_lines), "image_output": image_output}
    except Exception as inst:
        return {"text_output": traceback.format_exc(), "image_output": ""}
    finally:
        if tmp_dir_path:
            shutil.rmtree(tmp_dir_path, ignore_errors=True)

def encode_image_bytes(b):
    return str(base64.b64encode(b), "utf-8")

# From https://stackoverflow.com/questions/12485666/python-deleting-all-files-in-a-folder-older-than-x-days
def remove_old_temp_dirs(dir_path):
    criticalTime = arrow.now().shift(minutes=-5)

    for item in Path(dir_path).glob("*"):
        itemTime = arrow.get(item.stat().st_mtime)
        if itemTime < criticalTime:
            shutil.rmtree(item, ignore_errors=True)
