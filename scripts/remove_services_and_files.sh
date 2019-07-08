#!/usr/bin/env bash
CONFIG_DIR="/etc/kootnet"
USER_DIR="/home/pi"
DATA_DIR="/home/kootnet_data"
SPECIAL_SCRIPTS_DIR="/home/kootnet_data/scripts"
printf '\nDisabling & stopping all sensor services\n\n'
systemctl disable KootnetSensors
systemctl stop KootnetSensors
# Remove following 4 lines after version 25.38
systemctl disable SensorCommands
systemctl disable SensorRecording
systemctl stop SensorCommands
systemctl stop SensorRecording
printf '\nRemoving sensor service files\n'
rm -f /etc/systemd/system/KootnetSensors.service 2>/dev/null
# Remove following 2 lines after Version 25.38
rm -f /etc/systemd/system/SensorCommands.service 2>/dev/null
rm -f /etc/systemd/system/SensorRecording.service 2>/dev/null
printf '\nRemoving Program Files\n'
rm -R -f /opt/kootnet-sensors 2>/dev/null
rm -f -R /opt/kootnet-sensors
rm -f ${SPECIAL_SCRIPTS_DIR}/clean_upgrade_online.sh 2>/dev/null
rm -f ${SPECIAL_SCRIPTS_DIR}/clean_upgrade_smb.sh 2>/dev/null
rm -f /usr/share/applications/KootNet-Sensor-Config.desktop
sleep 4
