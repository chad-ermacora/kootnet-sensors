#!/bin/bash
# Make sure its running with root
if [[ $EUID != 0 ]]; then
  printf "\nStarting with sudo\n"
  sudo "$0" "$@"
  exit $?
fi
/home/kootnet_data/env/bin/python /opt/kootnet-sensors/change_http_auth_credentials.py
systemctl restart KootnetSensors 2>/dev/null
