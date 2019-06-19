#!/usr/bin/env bash
# Upgrade from Online HTTP server
DATA_DIR="/home/kootnet_data"  # This is hardcoded into linux services
CONFIG_DIR="/etc/kootnet"
# HTTP Server Options
HTTP_SERVER="http://kootenay-networks.com"
HTTP_FOLDER="/utils/koot_net_sensors/Installers/raspbian"
HTTP_ZIP="/KootNetSensors.zip"
CONTROL_INSTALL="n"
# Make sure its running with root
clear
if [[ $EUID != 0 ]]; then
  printf "\nStarting with sudo\n"
  sudo "$0" "$@"
  exit $?
fi
# Kill any open nano & make sure folders are created
killall nano 2>/dev/null
printf '\nChecking & Creating Required Folders\n'
mkdir ${DATA_DIR} 2>/dev/null
mkdir ${DATA_DIR}/logs 2>/dev/null
mkdir ${DATA_DIR}/scripts 2>/dev/null
mkdir ${CONFIG_DIR} 2>/dev/null
mkdir ${CONFIG_DIR}/backups 2>/dev/null
mkdir /opt/kootnet-sensors 2>/dev/null
mkdir /opt/kootnet-sensors/auto_start 2>/dev/null
mkdir /opt/kootnet-sensors/sensor_modules 2>/dev/null
mkdir /opt/kootnet-sensors/scripts 2>/dev/null
# Clean up previous downloads if any
rm -R /tmp/SensorHTTPUpgrade 2>/dev/null
rm -f /tmp/KootNetSensors.zip 2>/dev/null
mkdir /tmp/SensorHTTPUpgrade 2>/dev/null
# Download and Upgrade Sensor Programs
if [[ -f /opt/kootnet-control-center/requirements.txt ]]
then
  echo
else
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
fi
printf '\n\nDownload Started\n'
wget -q --show-progress ${HTTP_SERVER}${HTTP_FOLDER}${HTTP_ZIP} -P /tmp/
printf 'Download Complete\n\nUnzipping & Installing Files\n'
unzip -q /tmp/KootNetSensors.zip -d /tmp/SensorHTTPUpgrade
cp -f -R /tmp/SensorHTTPUpgrade/sensor-rp/* /opt/kootnet-sensors
printf 'Files Installed\n\n'
bash /opt/kootnet-sensors/scripts/chk_install.sh
# Install Control Center requirements
if [[ ${CONTROL_INSTALL} =~ ^[Yy]$ ]]
then
  printf '\nInstalling Control Center Requirements & Desktop Shortcut\n'
  mkdir /opt/kootnet-control-center 2>/dev/null
  mkdir /opt/kootnet-control-center/logs 2>/dev/null
  cp -f -R /tmp/SensorHTTPUpgrade/sensor-control-center/* /opt/kootnet-control-center
  bash /opt/kootnet-control-center/scripts/create_shortcuts.sh ${USER_NAME}
  bash /opt/kootnet-control-center/scripts/create_custom_uninstall.sh ${USER_NAME}
  source ${DATA_DIR}/python-env/bin/activate
  pip3 install -r /opt/kootnet-control-center/requirements.txt
  deactivate
  printf '\nControl Center Requirements Installed\n\n'
elif [[ -f /opt/kootnet-control-center/requirements.txt ]]
then
  printf '\nUpgrading Control Center Install\n\n'
  cp -f -R /tmp/SensorHTTPUpgrade/sensor-control-center/* /opt/kootnet-control-center
fi
# Updating Clean Upgrade files
cp -f /opt/kootnet-sensors/scripts/clean_upgrade_online.sh ${DATA_DIR}/scripts
cp -f /opt/kootnet-sensors/scripts/clean_upgrade_smb.sh ${DATA_DIR}/scripts
cp -f /opt/kootnet-sensors/scripts/uninstall.sh ${DATA_DIR}/scripts
# Add easy Configuration editing to users home directory
if [[ -f ${CONFIG_DIR}/installed_datetime.txt ]]
then
  echo
else
  bash /opt/kootnet-sensors/scripts/copy_shortcuts.sh ${USER_NAME}
fi
# Update & Enable Auto Start Applications. Set Wireless Networks. Set File Permissions
bash /opt/kootnet-sensors/scripts/set_autostart.sh
bash /opt/kootnet-sensors/scripts/set_permissions.sh
# Save datetime to last updated file
date > ${CONFIG_DIR}/last_updated.txt
echo ' - HTTP ' >> ${CONFIG_DIR}/last_updated.txt
printf '\nDone\n\n'
systemctl restart SensorCommands
