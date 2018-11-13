#!/usr/bin/env bash
DATA_DIR="/home/kootnet_data"
CONFIG_DIR="/etc/kootnet"
# Make sure log files exist to set permissions
touch /opt/kootnet-control-center/config.txt
touch /opt/kootnet-control-center/logs/KootNet_log.txt
touch /opt/kootnet-control-center/logs/Sensor_Commands_log.txt
touch ${DATA_DIR}/logs/Primary_log.txt
touch ${DATA_DIR}/logs/Sensors_log.txt
touch ${DATA_DIR}/logs/Network_log.txt
# Set group to all users
chown :users ${DATA_DIR} -R
chown :users ${CONFIG_DIR} -R
# Make sure permissions are correct
printf '\nSetting permissions\n'
chmod 775 ${DATA_DIR} -R
chmod 754 ${DATA_DIR}/scripts/*
chmod 775 ${CONFIG_DIR} -R
chmod 775 /opt/kootnet-sensors -R
chmod 775 /opt/kootnet-control-center -R
chmod 777 /opt/kootnet-control-center/config.txt
chmod 777 /opt/kootnet-control-center/logs/*.txt
chmod 777 /var/log/lighttpd -R 2>/dev/null
