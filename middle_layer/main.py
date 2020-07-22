import base64
from fastapi import FastAPI, HTTPException
import getpass
import os
from pydantic import BaseModel
import shutil
import subprocess
import tempfile
import traceback

class ExecInfo(BaseModel):
    image_name: str
    code: str
    memory_allowed_mb: int
    timeout_seconds: int
    output_type: str

app = FastAPI()

@app.get("/hello")
def hello():
    return "World"

@app.post("/exec/")
def exec(info: ExecInfo):
    base_tmp_dir_path = f"/tmp/codebuddy_backend_{getpass.getuser()}"
    os.makedirs(base_tmp_dir_path, exist_ok=True)
    tmp_dir_path = tempfile.mkdtemp(dir=base_tmp_dir_path)
    cpus = 1

    try:
        # Save the user's code to a file that will be accessible inside the container.
        with open(f"{tmp_dir_path}/code", "w") as the_file:
            the_file.write(info.code)

        # About --cap-drop: https://www.redhat.com/en/blog/secure-your-containers-one-weird-trick
        #docker_command = f"timeout -s 9 {info.timeout_seconds}s docker run --rm --user $(id -u):$(id -g) --cpus {cpus} --memory={info.memory_allowed_mb}m --cap-drop=ALL --read-only=true --log-driver=none --workdir /sandbox -v {tmp_dir_path}/:/sandbox/ {info.image_name} /sandbox/code {info.output_type}"
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
        shutil.rmtree(tmp_dir_path, ignore_errors=True)

    return {"output": output, "error_occurred": error_occurred}

def encode_image_bytes(b):
    return str(base64.b64encode(b), "utf-8")
