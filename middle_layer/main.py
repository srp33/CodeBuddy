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
    base_tmp_dir_path = os.path.join(tempfile.gettempdir(), f"codebuddy_backend")
    #/tmp/codebuddy_backend_{getpass.getuser()}"
    cpus = 1
    tmp_dir_path = None

    # We specify the maximum characters to read. This avoids people bogging
    # down the server with really long outputs.
    MAX_OUTPUT_LENGTH = 100 * 1024

    try:
        # This is meant to identify any old temp directories that inadvertently were not deleted.
        # This is not the best design, but it is simple.
        # It means we don't need to configure a separate process to run in the background.
        remove_old_temp_dirs(base_tmp_dir_path)

        os.makedirs(base_tmp_dir_path, exist_ok=True)
        tmp_dir_path = tempfile.mkdtemp(dir=base_tmp_dir_path)

        # Save the verification code to a file that will be accessible inside the container.
        do_verification = len(info.verification_code.strip()) > 0

        if do_verification:
            with open(os.path.join(tmp_dir_path, "verification_code"), "w") as verification_file:
                verification_file.write(info.verification_code)

        # Save information for each test under a subdirectory under 'tests'.
        for test_title in info.tests:
            info.tests[test_title]["dir_path"] = os.path.join(tmp_dir_path, "tests", test_title)
            os.makedirs(info.tests[test_title]["dir_path"], exist_ok=True)

            with open(os.path.join(info.tests[test_title]['dir_path'], "before_code"), "w") as code_file:
                if info.tests[test_title]["before_code"].strip() != "":
                    code_file.write(info.tests[test_title]["before_code"].strip() + "\n\n")

            with open(os.path.join(info.tests[test_title]['dir_path'], "main_code"), "w") as code_file:
                code_file.write(info.code.strip() + "\n\n")

            with open(os.path.join(info.tests[test_title]['dir_path'], "after_code"), "w") as code_file:
                if info.tests[test_title]["after_code"].strip() != "":
                    code_file.write(info.tests[test_title]["after_code"].strip() + "\n\n")

            # Save any data files so they will be accessible inside the container.
            for file_name, contents in info.data_files.items():
                if not file_name.endswith(".hide") or (info.tests[test_title]["can_see_test_code"] == False and info.tests[test_title]["can_see_expected_output"] == False and info.tests[test_title]["can_see_code_output"] == False):
                    with open(os.path.join(info.tests[test_title]['dir_path'], file_name), "w") as data_file:
                        data_file.write(contents)

        if info.timeout_seconds <= 0:
            # This is used for debugging in development mode.
            docker_command = f"docker run --rm --workdir /sandbox -v {tmp_dir_path}:/sandbox {info.image_name}:latest {do_verification} {info.output_type}"
        else:
            # About --cap-drop: https://www.redhat.com/en/blog/secure-your-containers-one-weird-trick
            docker_command = f"timeout -s 9 {info.timeout_seconds}s docker run --rm --user $(id -u):$(id -g) --ulimit cpu={info.timeout_seconds} --cpus {cpus} --memory={info.memory_allowed_mb}m --cap-drop=ALL --network=none --log-driver=none --workdir /sandbox -v {tmp_dir_path}/:/sandbox/ {info.image_name}:latest {do_verification} {info.output_type}"

        result = subprocess.run(docker_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        docker_warning = "WARNING: Your kernel does not support swap limit capabilities or the cgroup is not mounted. Memory limited without swap."
        stdout = result.stdout.decode().replace(docker_warning, "")

        # Check whether the command timed out.
        if result.returncode == 137 or stdout == "Killed" and info.timeout_seconds > 0:
            raise Exception(f"The time to execute your code exceeded the timeout ({info.timeout_seconds} seconds) or was unable to complete for some other reason.")

        if result.returncode != 0:
            if stdout.strip() == "":
                stdout = "[No output was detected.]"

            raise Exception(f"The following error occurred on the back end: {stdout}.")

        test_outputs = {}

        for test_title in info.tests:
            txt_output = ""
            txt_output_file_path = os.path.join(info.tests[test_title]['dir_path'], "txt_output")

            if os.path.exists(txt_output_file_path):
                txt_output_file_size = os.path.getsize(txt_output_file_path)

                if txt_output_file_size > 0:
                    with open(txt_output_file_path) as output_file:
                        txt_output = output_file.read(MAX_OUTPUT_LENGTH).strip()

                        if txt_output_file_size > MAX_OUTPUT_LENGTH:
                            txt_output += "\n[The output was truncated...]"

            jpg_output = ""
            if info.output_type == "jpg":
                jpg_output_file_path = os.path.join(info.tests[test_title]['dir_path'], "jpg_output")

                if os.path.exists(jpg_output_file_path) and os.path.getsize(jpg_output_file_path) > 0:
                    if os.path.getsize(jpg_output_file_path) > MAX_OUTPUT_LENGTH:
                        txt_output += "\n[The image was truncated...]"
                    else:
                        with open(jpg_output_file_path, "rb") as output_file:
                            jpg_output = encode_image_bytes(output_file.read())

            test_outputs[test_title] = {"txt_output": txt_output, "jpg_output": jpg_output}
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
