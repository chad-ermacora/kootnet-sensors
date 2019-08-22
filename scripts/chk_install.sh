#!/usr/bin/env bash
# HTTP Download Server Options
APT_GET_INSTALL="python3-pip python3-venv libatlas3-base fonts-freefont-ttf sense-hat fake-hwclock cifs-utils libfreetype6-dev libjpeg-dev build-essential openssl"
DATA_DIR="/home/kootnet_data"  # This is hardcoded into linux services
CONFIG_DIR="/etc/kootnet"
# Network + Other Setup
if [[ -f ${CONFIG_DIR}"/installed_datetime.txt" ]]
then
  printf '\nPrevious install detected, skipping setup\n'
else
  # Install needed programs and dependencies
  printf '\nEnabling SPI, i2c & Wireless\n\n'
  raspi-config nonint do_i2c 0
  raspi-config nonint do_spi 0
  rfkill unblock wifi
  printf '\nStarting Dependency Install. This may take awhile ...\n\n'
  apt-get update
  apt-get -y install ${APT_GET_INSTALL}
  cd ${DATA_DIR} || exit
  python3 -m venv --system-site-packages python-env
  source ${DATA_DIR}/python-env/bin/activate
  python3 -m pip install -U pip
  pip3 install -r /opt/kootnet-sensors/requirements.txt
  # Set HTTP Authentication
  clear
  printf 'Dependencies Installed\n\n'
  bash /opt/kootnet-sensors/scripts/change_http_authentication.sh
  cat > ${CONFIG_DIR}/installed_version.txt << "EOF"
New_Install.99.999
EOF
  deactivate
  # Create Installed File to prevent re-runs.  Create install_version file for program first run.
  date > ${CONFIG_DIR}/installed_datetime.txt
fi
