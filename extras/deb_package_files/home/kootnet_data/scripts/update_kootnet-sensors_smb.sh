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
DEB_INSTALLER="/KootnetSensors.deb"
MOUNT_DIR="/mnt/supernas"
CIFS_OPTIONS="username=myself,password='123'"
CONFIG_DIR="/etc/kootnet"
INSTALL_TYPE="Standard"
# Check for Development option
if [[ "$1" == "dev" ]]; then
  DEB_INSTALLER="/dev/KootnetSensors.deb"
  INSTALL_TYPE="Developmental"
fi
printf '\n-- %s SMB UPGRADE OR INSTALL --\n' "${INSTALL_TYPE}"
mkdir ${MOUNT_DIR} 2>/dev/null
mount -t cifs ${SMB_SERVER}${SMB_SHARE} ${MOUNT_DIR} -o ${CIFS_OPTIONS}
sleep 1
apt-get -y install ${MOUNT_DIR}${DEB_INSTALLER}
umount ${MOUNT_DIR}
# Save DateTime and Update type to file (Used in program to show last updated)
date >${CONFIG_DIR}/last_updated.txt
echo ' - SMB' >>${CONFIG_DIR}/last_updated.txt
