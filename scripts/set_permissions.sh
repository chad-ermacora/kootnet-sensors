#!/bin/bash
# This script resets permissions to a workable state, including access to most files as a regular user
DATA_DIR="/home/kootnet_data"
CONFIG_DIR="/etc/kootnet"
# Make sure log files exist to set permissions
touch ${DATA_DIR}/logs/Primary_log.txt
touch ${DATA_DIR}/logs/Sensors_log.txt
touch ${DATA_DIR}/logs/Network_log.txt
# Make sure permissions are correct
printf '\nSetting permissions\n'
chmod 755 ${DATA_DIR} -R
chmod 755 ${CONFIG_DIR}
chmod 744 ${CONFIG_DIR}/*
chmod 755 /opt/kootnet-sensors -R
# Make sure auth file exists to apply permissions to
if [ -f ${CONFIG_DIR}/auth.conf ]; then
  chmod 700 ${CONFIG_DIR}/auth.conf
fi
