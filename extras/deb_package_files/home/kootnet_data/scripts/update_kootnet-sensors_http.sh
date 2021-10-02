#!/bin/bash
# Make sure its running with root
if [[ $EUID != 0 ]]; then
  printf "\nStarting with sudo\n"
  sudo "$0" "$@"
  exit $?
fi
HTTP_SERVER="http://kootenay-networks.com"
HTTP_FOLDER="/installers"
DEB_INSTALLER="/KootnetSensors_online.deb"
CONFIG_DIR="/etc/kootnet"
INSTALL_TYPE="Standard"
# Check for development switch
if [[ "$1" == "dev" ]]; then
  HTTP_FOLDER="/installers/dev"
  INSTALL_TYPE="Developmental"
fi
clear
printf '%s HTTP Upgrade or Install\n\n' "${INSTALL_TYPE}"
printf 'Downloading installer ...\n\n'
# Clean up previous downloads if any
rm -f /tmp${DEB_INSTALLER} 2>/dev/null
wget -O /tmp${DEB_INSTALLER} ${HTTP_SERVER}${HTTP_FOLDER}${DEB_INSTALLER}
# Make sure the installer file is there
if [[ -s /tmp${DEB_INSTALLER} ]]; then
  printf 'Download complete\nStarting Upgrade\n\n'
  apt-get update
  apt-get -y install /tmp${DEB_INSTALLER}
  # Save DateTime and Update type to file (Used in program to show last updated)
  date -u >${CONFIG_DIR}/last_updated.txt
  echo ' - HTTP ' >>${CONFIG_DIR}/last_updated.txt
else
  printf '\nDownload failed, %s HTTP upgrade cancelled\n\n' "${INSTALL_TYPE}"
fi
