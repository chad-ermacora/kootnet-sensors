#!/usr/bin/env bash
CONFIG_DIR="/etc/kootnet"
# Make sure SMB_SHARE points to the root share holding the upgrade zip file
SMB_SERVER="//USB-Development"
DEB_INSTALLER="/KootnetSensors.deb"
# shellcheck disable=SC2089
CIFS_OPTIONS="username=myself,password='123'"
clear
# Make sure its running with root
if [[ $EUID != 0 ]]; then
  printf "\nStarting with sudo\n"
  sudo "$0" "$@"
  exit $?
fi
if [[ "$1" == "dev" ]]
then
  SMB_SHARE="/KootNetSMB/dev"
  printf '\n-- DEVELOPMENT SMB UPGRADE OR INSTALL --\n'
else
  printf '\n-- SMB UPGRADE OR INSTALL --\n'
  SMB_SHARE="/KootNetSMB"
fi
# Make sure folders are created
printf '\nChecking & Creating Required Folders\n'
mkdir /mnt 2>/dev/null
mkdir /mnt/supernas 2>/dev/null
# Clean up previous downloads if any
rm -f /tmp${DEB_INSTALLER} 2>/dev/null
# Mount share and copy file
mount -t cifs ${SMB_SERVER}${SMB_SHARE} /mnt/supernas -o ${CIFS_OPTIONS}
sleep 1
printf '\n\nDownload Started\n'
cp /mnt/supernas${DEB_INSTALLER} /tmp
apt-get -y install /tmp${DEB_INSTALLER}
# Save datetime to last updated file
date > ${CONFIG_DIR}/last_updated.txt
echo ' - SMB' >> ${CONFIG_DIR}/last_updated.txt
umount /mnt/supernas
