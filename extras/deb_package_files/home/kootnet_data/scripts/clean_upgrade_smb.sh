#!/bin/bash
# shellcheck disable=SC2089
# shellcheck disable=SC2090
# Make sure its running with root
if [[ $EUID != 0 ]]; then
  printf "\nStarting with sudo\n"
  sudo "$0" "$@"
  exit $?
fi
clear
SMB_SERVER="//USB-Development"
SMB_SHARE="/KootNetSMB"
DEB_INSTALLER="KootnetSensors.deb"
CIFS_OPTIONS="username=myself,password='123'"
CONFIG_DIR="/etc/kootnet/"
INSTALL_TYPE="Standard"
# Check for Development option
if [[ "$1" == "dev" ]]; then
  SMB_SHARE="/KootNetSMB/dev"
  INSTALL_TYPE="Developmental"
fi
printf '\n-- CLEAN %s SMB RE-INSTALL --\n' "${INSTALL_TYPE}"
printf '\nLeaving configurations and data, removing program folder and Python Virtual Environment\n\n'
mkdir /mnt 2>/dev/null
mkdir /mnt/supernas 2>/dev/null
mkdir /tmp 2>/dev/null
rm -f /tmp/${DEB_INSTALLER} 2>/dev/null
mount -t cifs ${SMB_SERVER}${SMB_SHARE} /mnt/supernas -o ${CIFS_OPTIONS}
sleep 1
cp /mnt/supernas/${DEB_INSTALLER} /tmp
sleep 1
umount /mnt/supernas
# Make sure the installer file is there before deleting everything
if [[ -f /tmp/${DEB_INSTALLER} ]]; then
  rm -R -f /home/kootnet_data/env 2>/dev/null
  rm -R -f /opt/kootnet-sensors 2>/dev/null
  rm -f /usr/share/applications/KootNet*.desktop 2>/dev/null
  rm -f /etc/systemd/system/Kootnet*.service 2>/dev/null
  rm -f /etc/systemd/system/SensorU*.service 2>/dev/null
  apt-get update
  apt-get -y --reinstall --allow-downgrades install /tmp/${DEB_INSTALLER}
  # Save DateTime and Update type to file (Used in program to show last updated)
  date -u >${CONFIG_DIR}last_updated.txt
  echo ' - Clean SMB ' >>${CONFIG_DIR}last_updated.txt
else
  printf '\nSMB Download Failed, Clean SMB ' "${INSTALL_TYPE}" ' Upgrade Cancelled\n'
fi
