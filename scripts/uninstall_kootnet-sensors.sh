#!/usr/bin/env bash
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
if [[ -f /opt/kootnet-control-center/requirements.txt ]]
then
  read -p "Would you like to Uninstall Control Center as well? (Y/N): " -n 1 -r CONTROL_UNINSTALL
fi
bash ${SPECIAL_SCRIPTS_DIR}/remove_services_and_files.sh
# Restore /etc/wpa_supplicant/wpa_supplicant.conf
if [[ -f ${CONFIG_DIR}"/backups/wpa_supplicant.conf" ]]
then
  printf 'Restoring original /etc/wpa_supplicant/wpa_supplicant.conf\n'
  cp -f ${CONFIG_DIR}/backups/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf 2>/dev/null
fi
# Uninstall Control Center
if [[ ${CONTROL_UNINSTALL} =~ ^[Yy]$ ]]
then
  bash ${SPECIAL_SCRIPTS_DIR}/control_center_uninstall.sh
fi
printf '\nRemoving easy access shortcuts\n'
rm -f /usr/share/applications/KootNet-Sensor-Config.desktop
rm -f /usr/share/applications/KootNet-Sensor-Web-Config.desktop
# Remove install check files & configurations
rm -f ${CONFIG_DIR}/installed_datetime.txt 2>/dev/null
rm -f ${CONFIG_DIR}/installed_sensors.conf 2>/dev/null
rm -f ${CONFIG_DIR}/sql_recording.conf 2>/dev/null
# Remove Misc. other
crontab -r
systemctl daemon-reload
printf '\n\nUninstall Complete.\nPress enter to exit\n'
read nothing2
rm -f ${SPECIAL_SCRIPTS_DIR}/remove_services_and_files.sh
rm -f ${SPECIAL_SCRIPTS_DIR}/uninstall_kootnet-sensors.sh
