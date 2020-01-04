#!/usr/bin/env bash
# Make sure SMB_SHARE points to the root share holding the upgrade zip file
SMB_SERVER="//USB-Development"
# shellcheck disable=SC2089
CIFS_OPTIONS="username=myself,password='123'"
DEB_INSTALLER="/KootnetSensors.deb"
CONFIG_DIR="/etc/kootnet"
clear
# Make sure its running with root
if [[ "$1" == "dev" ]]; then
  SMB_SHARE="/KootNetSMB/dev"
  printf '\n-- DEVELOPMENT CLEAN UPGRADE --\n'
else
  SMB_SHARE="/KootNetSMB"
fi
if [[ $EUID != 0 ]]; then
  printf "\nStarting with sudo\n"
  sudo "$0" "$@"
  exit $?
fi
# Start Script
mkdir /mnt 2>/dev/null
mkdir /mnt/supernas 2>/dev/null
printf '\n\nDoing "Clean" upgrade\nLeaves database & configs\nThen re-downloads and installs\n'
rm -f /tmp${DEB_INSTALLER} 2>/dev/null
rm -R -f /home/kootnet_data/env 2>/dev/null
rm -f ${CONFIG_DIR}/installed_datetime.txt
rm -R -f /opt/kootnet-sensors 2>/dev/null
# Mount SMB Share
mount -t cifs ${SMB_SERVER}${SMB_SHARE} /mnt/supernas -o ${CIFS_OPTIONS}
sleep 1
printf '\n\nDownload Started\n'
cp /mnt/supernas${DEB_INSTALLER} /tmp
apt-get -y --reinstall --allow-downgrades install /tmp${DEB_INSTALLER}
