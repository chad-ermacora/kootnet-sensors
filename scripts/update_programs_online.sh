#!/usr/bin/env bash
# Upgrade from Online HTTP server
SPECIAL_SCRIPTS_DIR="/home/kootnet_data/scripts"
CONFIG_DIR="/etc/kootnet"
# HTTP Server Options
HTTP_SERVER="http://kootenay-networks.com"
HTTP_FOLDER="/utils/koot_net_sensors/Installers/raspbian"
HTTP_ZIP="/KootNetSensors.zip"
# Make sure its running with root
clear
if [[ $EUID != 0 ]]; then
  printf "\nStarting with sudo\n"
  sudo "$0" "$@"
  exit $?
fi
# Start Script
if [[ -f "/opt/kootnet-sensors/scripts/chk_install.sh" ]]
then
  bash /opt/kootnet-sensors/scripts/chk_install.sh
else
  rm -f /tmp/chk_install.sh 2>/dev/null
  wget -nd ${HTTP_SERVER}${HTTP_FOLDER}/chk_install.sh -P /tmp/
  bash /tmp/chk_install.sh
fi
# Download and Upgrade Sensor Programs
rm -R /tmp/SensorHTTPUpgrade 2>/dev/null
mkdir /tmp/SensorHTTPUpgrade 2>/dev/null
rm -f /tmp/KootNetSensors.zip 2>/dev/null
printf '\n\nDownloads started\n'
wget ${HTTP_SERVER}${HTTP_FOLDER}${HTTP_ZIP} -P /tmp/
printf 'Downloads complete\nUnzipping & installing files\n'
unzip /tmp/KootNetSensors.zip -d /tmp/SensorHTTPUpgrade
cp -f -R /tmp/SensorHTTPUpgrade/sensor-rp/* /opt/kootnet-sensors
cp -f -R /tmp/SensorHTTPUpgrade/sensor-control-center/* /opt/kootnet-control-center
printf 'File install complete\n'
# Updating Clean Upgrade files
cp -f /opt/kootnet-sensors/scripts/clean_upgrade_online.sh ${SPECIAL_SCRIPTS_DIR}
cp -f /opt/kootnet-sensors/scripts/clean_upgrade_smb.sh ${SPECIAL_SCRIPTS_DIR}
cp -f /opt/kootnet-sensors/scripts/uninstall.sh ${SPECIAL_SCRIPTS_DIR}
# Add easy upgrade, config edits & sensor test app(s) to user pi's home directory
bash /opt/kootnet-sensors/scripts/copy_shortcuts.sh
# Update & Enable Auto Start Applications. Set Wireless Networks. Set File Permissions
bash /opt/kootnet-sensors/scripts/set_autostart.sh
bash /opt/kootnet-sensors/scripts/set_permissions.sh
# Save datetime to last updated file
date > ${CONFIG_DIR}/last_updated.txt
echo ' - HTTP ' >> ${CONFIG_DIR}/last_updated.txt
printf '\nDone\n\n'
systemctl restart SensorCommands
