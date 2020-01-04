#!/usr/bin/env bash
CONFIG_DIR="/etc/kootnet"
# Make sure its running with root
if [[ $EUID != 0 ]]; then
  printf "\nStarting with sudo\n"
  sudo "$0" "$@"
  exit $?
fi
# Change HTTP Authentication User & Password
read -p "Do you want to Change the HTTP Authentication? (Y/N) " -n 1 -r AUTH
echo
if [[ ${AUTH} =~ ^[Yy]$ ]]; then
  /home/kootnet_data/env/bin/python /opt/kootnet-sensors/change_http_auth_credentials.py
fi
# Open Config Files if installed
if [[ -f ${CONFIG_DIR}"/installed_datetime.txt" ]]; then
  printf "\nPrevious install detected, opening configuration files\n"
  nano ${CONFIG_DIR}/installed_sensors.conf
  nano ${CONFIG_DIR}/main_config.conf
  printf "\nRestarting Services, please wait ...\n\n"
  systemctl daemon-reload
  systemctl restart KootnetSensors
  counter=0
  while true; do
    if [[ "$(wget --no-check-certificate -q -O - "https://localhost:10065/CheckOnlineStatus")" == "OK" ]]; then
      printf "Printing config & testing sensors\n\n"
      /home/kootnet_data/env/bin/python /opt/kootnet-sensors/test_sensors.py
      printf "\nPress enter to exit ..."
      read -r nothing
      exit 0
    elif [ "$counter" -gt 30 ]; then
      printf "Timeout: The application did not start within 60 seconds, this may indicate a problem.\n\n"
      printf "Press enter to exit ..."
      read -r nothing
      exit 1
    fi
    sleep 2
    counter=$((counter + 1))
  done
fi
