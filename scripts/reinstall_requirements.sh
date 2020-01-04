#!/bin/bash
PYTHON_VENV_DIR="/home/kootnet_data/env"
APT_GET_INSTALL="python3 python3-pip python3-venv libatlas3-base fonts-freefont-ttf sense-hat fake-hwclock cifs-utils libfreetype6-dev libjpeg-dev build-essential"
apt-get update
apt-get -y install ${APT_GET_INSTALL}
rm -R ${PYTHON_VENV_DIR}
python3 -m venv --system-site-packages ${PYTHON_VENV_DIR}
${PYTHON_VENV_DIR}/bin/python -m pip install -U pip
${PYTHON_VENV_DIR}/bin/pip install -r /opt/kootnet-sensors/requirements.txt
