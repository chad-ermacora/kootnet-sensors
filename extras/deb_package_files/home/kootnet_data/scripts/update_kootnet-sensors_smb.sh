#!/bin/bash
# shellcheck disable=SC2089
# shellcheck disable=SC2090
# Make sure its running with root
if [[ $EUID != 0 ]]; then
  printf "\nStarting with sudo\n"
  sudo "$0" "$@"
  exit $?
fi
SMB_SERVER="//USB-Development"
SMB_SHARE="/KootNetSMB"
DEB_INSTALLER="/KootnetSensors_online.deb"
MOUNT_DIR="/mnt/supernas"
CIFS_OPTIONS="username=myself,password='123'"
CONFIG_DIR="/etc/kootnet"
INSTALL_TYPE="Standard"
# Check for Development option
if [[ "$1" == "dev" ]]; then
  SMB_SHARE="/KootNetSMB/dev"
  INSTALL_TYPE="Developmental"
fi
clear
printf '%s SMB Upgrade or Install\n\n' "${INSTALL_TYPE}"
printf 'Copying installer ...\n'
mkdir /mnt 2>/dev/null
mkdir /mnt/supernas 2>/dev/null
mkdir /tmp 2>/dev/null
rm -f /tmp${DEB_INSTALLER} 2>/dev/null
mount -t cifs ${SMB_SERVER}${SMB_SHARE} ${MOUNT_DIR} -o ${CIFS_OPTIONS}
sleep 1
cp ${MOUNT_DIR}${DEB_INSTALLER} /tmp
sleep 1
umount ${MOUNT_DIR}
# Make sure the installer file is there
if [[ -s /tmp${DEB_INSTALLER} ]]; then
  printf 'Copy complete\nStarting Upgrade\n\n'
  apt-get update
  apt-get -y install /tmp${DEB_INSTALLER}
  # Save DateTime and Update type to file (Used in program to show last updated)
  date -u >${CONFIG_DIR}/last_updated.txt
  echo ' - SMB' >>${CONFIG_DIR}/last_updated.txt
else
  printf '\nCopy failed, %s SMB upgrade cancelled\n\n' "${INSTALL_TYPE}"
fi
