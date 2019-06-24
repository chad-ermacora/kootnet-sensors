#!/usr/bin/env bash
# Upgrade from SMB server (Windows Share)
DATA_DIR="/home/kootnet_data"  # This is hardcoded into linux services
CONFIG_DIR="/etc/kootnet"
# Make sure SMB_SHARE points to the root share holding the upgrade zip file
SMB_SERVER="//xps-development01"
SMB_SHARE="/KootNetSMB"
SMB_FILE="/KootNetSensors.zip"
CIFS_OPTIONS="username=myself,password='123'"
# Make sure its running with root
clear
if [[ $EUID != 0 ]]; then
  printf "\nStarting with sudo\n"
  sudo "$0" "$@"
  exit $?
fi
# Make sure folders are created
printf '\nChecking & Creating Required Folders\n'
mkdir ${DATA_DIR} 2>/dev/null
mkdir ${DATA_DIR}/logs 2>/dev/null
mkdir ${DATA_DIR}/scripts 2>/dev/null
mkdir ${CONFIG_DIR} 2>/dev/null
mkdir ${CONFIG_DIR}/backups 2>/dev/null
mkdir /mnt/supernas 2>/dev/null
mkdir /opt/kootnet-sensors 2>/dev/null
mkdir /opt/kootnet-sensors/auto_start 2>/dev/null
mkdir /opt/kootnet-sensors/sensor_modules 2>/dev/null
mkdir /opt/kootnet-sensors/scripts 2>/dev/null
# Clean up previous downloads if any
rm -f /tmp/KootNetSensors.zip 2>/dev/null
rm -R /tmp/SensorSMBUpgrade 2>/dev/null
mkdir /tmp/SensorSMBUpgrade 2>/dev/null
# Start Script
if [[ -f ${CONFIG_DIR}/installed_datetime.txt ]]
then
  echo
else
  read -p "Do you want to Install Control Center as well? (Y/N) " -n 1 -r CONTROL_INSTALL
  echo
  if [[ ${CONTROL_INSTALL} =~ ^[Yy]$ ]]
    then
      read -p "Enter the username you want to create a desktop shortcut on (Default is pi): " USER_NAME
  fi
fi
# Make sure cifs is installed for SMB mount
apt-get install cifs-utils
printf '\nConnecting to SMB\n'
mount -t cifs ${SMB_SERVER}${SMB_SHARE} /mnt/supernas -o ${CIFS_OPTIONS}
sleep 1
printf '\n\nDownload Started\n'
cp /mnt/supernas${SMB_FILE} /tmp
unzip -q /tmp/KootNetSensors.zip -d /tmp/SensorSMBUpgrade
printf 'Download Complete\n\nUnzipping & Installing Files\n'
cp -f -R /tmp/SensorSMBUpgrade/sensor-rp/* /opt/kootnet-sensors
printf 'Files Installed\n\n'
# Add easy Configuration editing to users home directory
if [[ -f ${CONFIG_DIR}/installed_datetime.txt ]]
then
  echo
else
  bash /opt/kootnet-sensors/scripts/copy_shortcuts.sh ${USER_NAME}
fi
bash /opt/kootnet-sensors/scripts/chk_install.sh
# Install Control Center requirements
if [[ ${CONTROL_INSTALL} =~ ^[Yy]$ ]]
then
  printf '\nInstalling Control Center Requirements & Desktop Shortcut\n'
  mkdir /opt/kootnet-control-center 2>/dev/null
  mkdir /opt/kootnet-control-center/logs 2>/dev/null
  cp -f -R /tmp/SensorSMBUpgrade/sensor-control-center/* /opt/kootnet-control-center
  bash /opt/kootnet-control-center/scripts/install_dependencies.sh
  bash /opt/kootnet-control-center/scripts/create_shortcuts.sh ${USER_NAME}
  bash /opt/kootnet-control-center/scripts/create_custom_uninstall.sh ${USER_NAME}
  bash /opt/kootnet-control-center/scripts/set_permissions.sh
  printf '\nControl Center Requirements Installed\n\n'
elif [[ -f /opt/kootnet-control-center/requirements.txt ]]
then
  printf '\nUpgrading Control Center Install\n\n'
  cp -f -R /tmp/SensorSMBUpgrade/sensor-control-center/* /opt/kootnet-control-center
fi
# Updating Clean Upgrade files
cp -f /opt/kootnet-sensors/scripts/clean_upgrade_online.sh ${DATA_DIR}/scripts
cp -f /opt/kootnet-sensors/scripts/clean_upgrade_smb.sh ${DATA_DIR}/scripts
cp -f /opt/kootnet-sensors/scripts/uninstall.sh ${DATA_DIR}/scripts
# Update & Enable Auto Start Applications. Set Wireless Networks. Set File Permissions
bash /opt/kootnet-sensors/scripts/set_autostart.sh
bash /opt/kootnet-sensors/scripts/set_permissions.sh
# Save datetime to last updated file
date > ${CONFIG_DIR}/last_updated.txt
echo ' - SMB' >> ${CONFIG_DIR}/last_updated.txt
# Make sure SensorRecording service is up before restarting SensorCommands
sleep 5
printf '\nDone\n\n'
umount /mnt/supernas
systemctl restart SensorCommands
