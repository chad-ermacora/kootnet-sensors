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
chmod 766 ${DATA_DIR} -R
chmod 754 ${DATA_DIR}/scripts/*
chmod 766 ${CONFIG_DIR} -R
chmod 754 /opt/kootnet-sensors -R
