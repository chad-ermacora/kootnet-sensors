#!/usr/bin/env bash
USER_DIR="/home/pi"
CONFIG_DIR="/etc/kootnet"
SPECIAL_SCRIPTS_DIR="/home/kootnet_data/scripts"
# This script will remove all Sensor and Control Center program files off the Sensor, leaving configuration and data
if [[ $EUID != 0 ]]; then
  printf "\nStarting with sudo\n"
  sudo "$0" "$@"
  exit $?
fi
printf "\nThis will Uninstall all KootNet Sensors Software.\nPress enter to continue or CTRL + C to exit ..."
read nothing
printf '\nDisabling & stopping all sensor services\n'
systemctl disable SensorUpgradeChecks
systemctl disable SensorRecording
systemctl disable SensorCommands
systemctl disable SensorCleanUpgradeOnline
systemctl disable SensorCleanUpgradeSMB
systemctl stop SensorRecording
systemctl stop SensorCommands
printf '\nRemoving sensor service files\n'
rm -f /etc/systemd/system/SensorCommands.service 2>/dev/null
rm -f /etc/systemd/system/SensorRecording.service 2>/dev/null
rm -f /etc/systemd/system/SensorUpgradeChecks.service 2>/dev/null
rm -f /etc/systemd/system/SensorCleanUpgradeOnline.service 2>/dev/null
rm -f /etc/systemd/system/SensorCleanUpgradeSMB.service 2>/dev/null
# Restore /etc/network/interfaces & /etc/wpa_supplicant/wpa_supplicant.conf
if [[ -f ${CONFIG_DIR}"/backups/interfaces" ]]
then
  printf '\nRestoring original /etc/network/interfaces\n'
  cp -f ${CONFIG_DIR}/backups/interfaces /etc/network/interfaces 2>/dev/null
fi
if [[ -f ${CONFIG_DIR}"/backups/wpa_supplicant.conf" ]]
then
  printf 'Restoring original /etc/wpa_supplicant/wpa_supplicant.conf\n'
  cp -f ${CONFIG_DIR}/backups/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf 2>/dev/null
fi
printf '\nRemoving all Sensor & Control Center program files\n'
# Remove Sensor & Control Center program directories & files
killall python3 2>/dev/null
rm -f -R /opt/kootnet-sensors
rm -f ${SPECIAL_SCRIPTS_DIR}/clean_upgrade_online.sh 2>/dev/null
rm -f ${SPECIAL_SCRIPTS_DIR}/clean_upgrade_smb.sh 2>/dev/null
rm -f /usr/share/applications/KootNet-Sensor-Config.desktop
rm -f ${USER_DIR}/Desktop/KootNet-Sensor-Config.desktop
# Remove install check files & configurations
rm -f ${CONFIG_DIR}/installed_datetime.txt 2>/dev/null
rm -f ${CONFIG_DIR}/installed_sensors.conf 2>/dev/null
rm -f ${CONFIG_DIR}/sql_recording.conf 2>/dev/null
# Uninstall Control Center
bash /opt/kootnet-control-center/scripts/uninstall.sh
# Remove Misc. other
crontab -r
systemctl daemon-reload
printf '\n\nUninstall Complete.\nPress enter to exit\n'
read nothing2
rm -f ${SPECIAL_SCRIPTS_DIR}/uninstall.sh
