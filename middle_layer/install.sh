#! /bin/bash

#sudo apt update
#sudo apt install python3-pip
# sudo pip3 install arrow==0.13.1 fastapi==0.58.1 gunicorn==20.0.4 pydantic==1.5.1 uvicorn==0.11.5

# Debian-based systems
#sudo apt install python3-venv python3-dev build-essential

# Create a virtual environment
python3 -m venv myenv

# Activate it
source myenv/bin/activate

# Now pip install works normally
pip install arrow fastapi gunicorn pydantic uvicorn

#uvicorn
