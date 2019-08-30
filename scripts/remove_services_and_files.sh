#!/usr/bin/env bash
printf '\nDisabling & stopping all sensor services\n\n'
systemctl disable KootnetSensors
systemctl stop KootnetSensors
printf '\nRemoving sensor service files\n'
rm -f /etc/systemd/system/KootnetSensors.service 2>/dev/null
printf '\nRemoving Program Files\n'
rm -R -f /opt/kootnet-sensors 2>/dev/null

rm -f /usr/share/applications/KootNet-Sensor-Config.desktop
rm -f /usr/share/applications/KootNet-Sensor-Web-Config.desktop
sleep 1
