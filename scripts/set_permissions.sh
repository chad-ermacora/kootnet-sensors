#!/usr/bin/env bash
USER_DIR="/home/pi"
DATA_DIR="/home/kootnet_data"
CONFIG_DIR="/etc/kootnet"
# Make sure log files exist to set permissions
touch /opt/kootnet-control-center/config.txt 2>/dev/null
touch /opt/kootnet-control-center/logs/KootNet_log.txt 2>/dev/null
touch /opt/kootnet-control-center/logs/Sensor_Commands_log.txt 2>/dev/null
touch ${DATA_DIR}/logs/Primary_log.txt
touch ${DATA_DIR}/logs/Sensors_log.txt
touch ${DATA_DIR}/logs/Network_log.txt
# Make sure permissions are correct
printf '\nSetting permissions\n'
chmod 777 ${USER_DIR}/Desktop/*.desktop 2>/dev/null
chmod 777 ${DATA_DIR} -R
chmod 754 ${DATA_DIR}/scripts/*
chmod 777 ${CONFIG_DIR} -R
chmod 775 /opt/kootnet-sensors -R
chmod 775 /opt/kootnet-control-center -R 2>/dev/null
chmod 766 /opt/kootnet-control-center/config.txt 2>/dev/null
chmod 766 /opt/kootnet-control-center/logs/*.txt 2>/dev/null
