#!/bin/bash
# Make sure its running with root
if [[ $EUID != 0 ]]; then
  printf "\nStarting with sudo\n"
  sudo "$0" "$@"
  exit $?
fi
HTTP_SERVER="https://kootenay-networks.com"
HTTP_FOLDER="/installers/"
DEB_INSTALLER="KootnetSensors.deb"
CONFIG_DIR="/etc/kootnet/"
INSTALL_TYPE="Standard"
# Check for development switch
if [[ "$1" == "dev" ]]; then
  HTTP_FOLDER="/installers/dev/"
  INSTALL_TYPE="Developmental"
fi
clear
printf 'Clean %s HTTP Re-Install\n\n' "${INSTALL_TYPE}"
printf 'Downloading installer ...\n\n'
mkdir /tmp 2>/dev/null
rm -f /tmp/${DEB_INSTALLER} 2>/dev/null
wget -O /tmp/${DEB_INSTALLER} ${HTTP_SERVER}${HTTP_FOLDER}${DEB_INSTALLER}
# Make sure the installer file is there before deleting everything
if [[ -s /tmp/${DEB_INSTALLER} ]]; then
  printf 'Download complete\nRemoving old install (Configurations & data will be kept) ...\n'
  rm -R -f /home/kootnet_data/env 2>/dev/null
  rm -R -f /home/kootnet_data/ssl_files 2>/dev/null
  rm -R -f /opt/kootnet-sensors 2>/dev/null
  rm -f /usr/share/applications/KootNet*.desktop 2>/dev/null
  rm -f /etc/systemd/system/Kootnet*.service 2>/dev/null
  rm -f /etc/systemd/system/SensorU*.service 2>/dev/null
  printf 'Updating OS repository package lists ...\n\n'
  apt-get update
  printf '\nInstalling Kootnet Sensors ...\n\n'
  apt-get -y --reinstall --allow-downgrades install /tmp/${DEB_INSTALLER}
  # Save DateTime and Update type to file (Used in program to show last updated)
  date -u >${CONFIG_DIR}last_updated.txt
  echo ' - Clean HTTP ' >>${CONFIG_DIR}last_updated.txt
else
  printf '\nDownload failed, clean %s HTTP re-install cancelled\n\n' "${INSTALL_TYPE}"
fi
