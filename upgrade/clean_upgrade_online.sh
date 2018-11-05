clear
printf '\n\nDoing "Clean" upgrade\nLeaves database & config\nDeletes everything else\nThen re-downloads and installs\n'
cp /opt/kootnet-sensors/upgrade/update_programs_online.sh /root
printf '\nDisabling & stopping all sensor services\n'
systemctl disable SensorHTTP
systemctl disable SensorRecording
systemctl stop SensorHTTP
systemctl stop SensorRecording
# Remove these if updated beyond 21.10
systemctl disable SensorInterval
systemctl disable SensorTrigger
systemctl stop SensorInterval
systemctl stop SensorTrigger
printf '\nRemoving sensor service files\n'
rm -f /etc/systemd/system/SensorHTTP.service 2>/dev/null
rm -f /etc/systemd/system/SensorRecording.service 2>/dev/null
# Remove these if updated beyond 21.10
rm -f /etc/systemd/system/SensorInterval.service 2>/dev/null
rm -f /etc/systemd/system/SensorTrigger.service 2>/dev/null
printf '\nRemoving easy access shortcuts\n'
rm /home/pi/*.sh* 2>/dev/null
rm /home/pi/*.py* 2>/dev/null
rm -f /home/pi/Desktop/KootNet-Control-Center.desktop 2>/dev/null
printf '\nRemoving Program Files\n'
rm -R -f /opt/kootnet-sensors 2>/dev/null
rm -R -f /opt/kootnet-control-center 2>/dev/null
printf '\nStarting Upgrade in 4 seconds ...'
sleep 4
bash /root/update_programs_online.sh
