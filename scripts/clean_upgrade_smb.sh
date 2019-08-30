#!/usr/bin/env bash
CONFIG_DIR="/etc/kootnet"
clear
# Make sure its running with root
if [[ "$1" == "dev" ]]
then
  UPGRADE_DEV="dev"
  printf '\n-- DEVELOPMENT CLEAN UPGRADE --\n'
else
  UPGRADE_DEV=""
fi
if [[ $EUID != 0 ]]; then
  printf "\nStarting with sudo\n"
  sudo "$0" "$@"
  exit $?
fi
# Start Script
printf '\n\nDoing "Clean" upgrade\nLeaves database & config\nDeletes everything else\nThen re-downloads and installs\n'
cp -f /opt/kootnet-sensors/scripts/remove_services_and_files.sh /root
cp -f /opt/kootnet-sensors/scripts/install_update_kootnet-sensors_smb.sh /root
bash /root/remove_services_and_files.sh
rm -R -f /home/kootnet_data/python-env 2>/dev/null
rm -f ${CONFIG_DIR}/installed_datetime.txt
bash /root/install_update_kootnet-sensors_smb.sh ${UPGRADE_DEV}
