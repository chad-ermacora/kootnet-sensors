#!/usr/bin/env bash
DATA_DIR="/home/kootnet_data"  # This is hardcoded into linux services
APT_GET_INSTALL="python3-pip python3-venv libatlas3-base fonts-freefont-ttf sense-hat fake-hwclock cifs-utils libfreetype6-dev libjpeg-dev build-essential"
apt-get update
apt-get -y install ${APT_GET_INSTALL}
cd ${DATA_DIR}
python3 -m venv --system-site-packages python-env
source ${DATA_DIR}/python-env/bin/activate
python3 -m pip install -U pip
pip3 install -r /opt/kootnet-sensors/requirements.txt
deactivate
