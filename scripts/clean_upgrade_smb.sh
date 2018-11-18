#!/usr/bin/env bash
USER_DIR="/home/pi/"
# Make sure its running with root
clear
if [[ $EUID != 0 ]]; then
  printf "\nStarting with sudo\n"
  sudo "$0" "$@"
  exit $?
fi
# Start Script
printf '\n\nDoing "Clean" upgrade\nLeaves database & config\nDeletes everything else\nThen re-downloads and installs\n'
cp -f /opt/kootnet-sensors/scripts/update_programs_smb.sh /root
printf '\nDisabling & stopping all sensor services\n'
systemctl disable SensorCommands
systemctl disable SensorHTTP
systemctl disable SensorRecording
systemctl stop SensorCommands
systemctl stop SensorHTTP
systemctl stop SensorRecording
printf '\nRemoving sensor service files\n'
rm -f /etc/systemd/system/SensorCommands.service 2>/dev/null
rm -f /etc/systemd/system/SensorHTTP.service 2>/dev/null
rm -f /etc/systemd/system/SensorRecording.service 2>/dev/null
printf '\nRemoving easy access shortcuts\n'
rm -f ${USER_DIR}/Desktop/KootNet-Control-Center.desktop 2>/dev/null
rm -f ${USER_DIR}/Desktop/KootNet-Sensor-Config.desktop 2>/dev/null
rm -f /usr/share/applications/KootNet-Control-Center.desktop
rm -f /usr/share/applications/KootNet-Sensor-Config.desktop
printf '\nRemoving Program Files\n'
rm -R -f /opt/kootnet-sensors 2>/dev/null
rm -R -f /opt/kootnet-control-center 2>/dev/null
printf '\nStarting Upgrade in 4 seconds ...'
sleep 4
bash /root/update_programs_smb.sh
