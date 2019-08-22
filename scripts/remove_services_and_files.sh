#!/usr/bin/env bash
SPECIAL_SCRIPTS_DIR="/home/kootnet_data/scripts"
printf '\nDisabling & stopping all sensor services\n\n'
systemctl disable KootnetSensors
systemctl stop KootnetSensors
printf '\nRemoving sensor service files\n'
rm -f /etc/systemd/system/KootnetSensors.service 2>/dev/null
printf '\nRemoving Program Files\n'
rm -R -f /opt/kootnet-sensors 2>/dev/null
rm -f ${SPECIAL_SCRIPTS_DIR}/clean_upgrade_http.sh 2>/dev/null
rm -f ${SPECIAL_SCRIPTS_DIR}/clean_upgrade_smb.sh 2>/dev/null
rm -f /usr/share/applications/KootNet-Sensor-Config.desktop
rm -f /usr/share/applications/KootNet-Sensor-Web-Config.desktop
sleep 4
