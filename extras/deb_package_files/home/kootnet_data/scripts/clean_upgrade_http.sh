#!/usr/bin/env bash
HTTP_SERVER="http://kootenay-networks.com"
DEB_INSTALLER="/KootnetSensors.deb"
CONFIG_DIR="/etc/kootnet"
clear
# Make sure its running with root
if [[ "$1" == "dev" ]]
then
  HTTP_FOLDER="/installers/dev"
  printf '\n-- DEVELOPMENT CLEAN UPGRADE --\n'
else
  HTTP_FOLDER="/installers"
fi
if [[ $EUID != 0 ]]; then
  printf "\nStarting with sudo\n"
  sudo "$0" "$@"
  exit $?
fi
# Start Script
printf '\n\nDoing "Clean" upgrade\nLeaves database & configs\nThen re-downloads and installs\n'
rm -f /tmp${DEB_INSTALLER} 2>/dev/null
rm -R -f /home/kootnet_data/env 2>/dev/null
rm -f ${CONFIG_DIR}/installed_datetime.txt
rm -R -f /opt/kootnet-sensors 2>/dev/null
wget -O /tmp${DEB_INSTALLER} ${HTTP_SERVER}${HTTP_FOLDER}${DEB_INSTALLER}
apt-get -y --allow-downgrades --reinstall install /tmp${DEB_INSTALLER}
