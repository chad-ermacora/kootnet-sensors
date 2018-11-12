#!/usr/bin/env bash
# Open Config Files if installed
if [[ -f "/home/pi/KootNetSensors/zInstalled.txt" ]]
then
  printf '\nPrevious install detected, opening configuration files\n'
  nano /home/pi/KootNetSensors/installed_sensors.txt
  nano /home/pi/KootNetSensors/config.txt
  nano /etc/network/interfaces
  nano /etc/wpa_supplicant/wpa_supplicant.conf
  printf '\nPrinting config & testing sensors\n\n'
  killall python3
  python3 /opt/kootnet-sensors/test_sensors.py
fi
