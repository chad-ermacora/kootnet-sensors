#!/usr/bin/env bash
# Upgrade from SMB server (Windows Share)
SPECIAL_SCRIPTS_DIR="/home/kootnet_data/scripts"
CONFIG_DIR="/etc/kootnet"
# Make sure SMB_SHARE points to the root share holding both Sensor & Control Center folders
SMB_SERVER="//gamercube1"
SMB_SHARE="/PyCharmProjects"
SMB_SENSOR="/sensor-rp"
SMB_CONTROL_CENTER="/sensor-control-center"
CIFS_OPTIONS="username=myself,password='123'"
RSYNC_EXCLUDE="--exclude .git --exclude .idea --exclude __pycache__ --exclude config.txt --exclude logs/KootNet_log.txt --exclude logs/Sensor_Commands_log.txt --exclude test_files/SensorIntervalGraph.html --exclude test_files/SensorTriggerGraph.html"
# Make sure its running with root
clear
if [[ $EUID != 0 ]]; then
  printf "\nStarting with sudo\n"
  sudo "$0" "$@"
  exit $?
fi
# Start Script
if [[ -f "/opt/kootnet-sensors/upgrade/chk_install.sh" ]]
then
  bash /opt/kootnet-sensors/upgrade/chk_install.sh
else
  mkdir /mnt/supernas 2>/dev/null
  mount -t cifs ${SMB_SERVER}${SMB_SHARE} /mnt/supernas -o ${CIFS_OPTIONS}
  sleep 1
  bash /mnt/supernas/sensor-rp/upgrade/chk_install.sh
  umount /mnt/supernas
  printf '\nProceeding with SMB upgrade\n'
fi
# Download and Upgrade Sensor Programs off SMB
printf '\nConnecting to SMB & copying files\n'
mount -t cifs ${SMB_SERVER}${SMB_SHARE} /mnt/supernas -o ${CIFS_OPTIONS}
sleep 1
printf 'Copying sensor files\n'
rsync -q -r -4 -P /mnt/supernas${SMB_SENSOR}/ /opt/kootnet-sensors/ ${RSYNC_EXCLUDE}
printf 'Copying control center files\n\n'
rsync -q -r -4 -P /mnt/supernas${SMB_CONTROL_CENTER}/ /opt/kootnet-control-center/ ${RSYNC_EXCLUDE}
sleep 1
umount /mnt/supernas
# Updating Clean Upgrade files
cp -f /opt/kootnet-sensors/upgrade/clean_upgrade_online.sh ${SPECIAL_SCRIPTS_DIR}
cp -f /opt/kootnet-sensors/upgrade/clean_upgrade_smb.sh ${SPECIAL_SCRIPTS_DIR}
# Add easy upgrade, config edits & sensor test app(s) to user pi's home directory
bash /opt/kootnet-sensors/upgrade/copy_shortcuts.sh
# Update & Enable Auto Start Applications. Set Wireless Networks. Set File Permissions
bash /opt/kootnet-sensors/upgrade/set_autostart.sh
bash /opt/kootnet-sensors/upgrade/set_permissions.sh
# Save datetime to last updated file
date > ${CONFIG_DIR}/last_updated.txt
echo ' - SMB' >> ${CONFIG_DIR}/last_updated.txt
printf '\nDone\n\n'
systemctl restart SensorCommands
