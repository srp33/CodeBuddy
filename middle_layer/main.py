import arrow
import base64
from fastapi import FastAPI, HTTPException
import getpass
import os
from pathlib import Path
from pydantic import BaseModel
import shutil
import subprocess
import tempfile
import traceback

class ExecInfo(BaseModel):
    image_name: str
    code: str
    data_file_name: str
    data_contents: str
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
        # This is not the best design, but we do it this way for simplicity.
        # It means we don't need to configure a separate process to run in the background.
        # And it should be fast enough.
        remove_old_temp_dirs(base_tmp_dir_path)

        os.makedirs(base_tmp_dir_path, exist_ok=True)
        tmp_dir_path = tempfile.mkdtemp(dir=base_tmp_dir_path)

        # Save the user's code to a file that will be accessible inside the container.
        with open(f"{tmp_dir_path}/code", "w") as code_file:
            code_file.write(info.code)

        if info.data_file_name != "":
            with open(f"{tmp_dir_path}/{info.data_file_name}", "w") as data_file:
                data_file.write(info.data_contents)

        # About --cap-drop: https://www.redhat.com/en/blog/secure-your-containers-one-weird-trick
        docker_command = f"timeout -s 9 {info.timeout_seconds}s docker run --rm --user $(id -u):$(id -g) --cpus {cpus} --memory={info.memory_allowed_mb}m --cap-drop=ALL --log-driver=none --workdir /sandbox -v {tmp_dir_path}/:/sandbox/ {info.image_name} /sandbox/code {info.output_type}"

        result = subprocess.run(docker_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        error_occurred = False

        if os.path.exists(f"{tmp_dir_path}/error"):
            with open(f"{tmp_dir_path}/error", "r") as error_file:
                output = error_file.read()

            if len(output) > 0:
                error_occurred = True

        if not error_occurred:
            timed_out = result.returncode == 137
            if timed_out:
                error_occurred = True
                output = f"The time to execute your code exceeded {infotimeout_seconds} seconds."
            else:
                error_occurred = result.returncode > 0
                if error_occurred:
                    output = "ERROR: " + result.stdout.rstrip().decode()

                    # Docker displays this, but we can ignore it.
                    #output_to_ignore = "WARNING: Your kernel does not support swap limit capabilities or the cgroup is not mounted. Memory limited without swap."
                    #output = "\n".join([line for line in result.stdout.rstrip().decode().split("\n") if line != output_to_ignore])
                else:
                    if info.output_type == "txt":
                        with open(f"{tmp_dir_path}/output", "r") as output_file:
                            output = output_file.read()
                    else:
                        with open(f"{tmp_dir_path}/output", "rb") as output_file:
                            output = encode_image_bytes(output_file.read())
    except Exception as inst:
        error_occurred = True
        output = traceback.format_exc()
    finally:
        if tmp_dir_path:
            shutil.rmtree(tmp_dir_path, ignore_errors=True)

    return {"output": output, "error_occurred": error_occurred}

def encode_image_bytes(b):
    return str(base64.b64encode(b), "utf-8")

# From https://stackoverflow.com/questions/12485666/python-deleting-all-files-in-a-folder-older-than-x-days
def remove_old_temp_dirs(dir_path):
    criticalTime = arrow.now().shift(minutes=-5)

    for item in Path(dir_path).glob("*"):
        itemTime = arrow.get(item.stat().st_mtime)
        if itemTime < criticalTime:
            shutil.rmtree(item, ignore_errors=True)
