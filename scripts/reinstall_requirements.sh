#!/usr/bin/env bash
DATA_DIR="/home/kootnet_data"  # This is hardcoded into linux services
python3 -m venv --system-site-packages python-env
source ${DATA_DIR}/python-env/bin/activate
python3 -m pip install -U pip
pip3 install -r /opt/kootnet-sensors/requirements.txt
deactivate
