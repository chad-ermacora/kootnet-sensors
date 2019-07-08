#!/usr/bin/env bash
printf 'Setting fake-hwclock to run every 1 min in root crontab\n\n'
echo '*/1 * * * * fake-hwclock' >> /tmp/tmp34441.txt
crontab -u root /tmp/tmp34441.txt
rm /tmp/tmp34441.txt
printf 'Recopying, enabling and restarting KootNet sensor services\n'
cp -f /opt/kootnet-sensors/auto_start/*.service /etc/systemd/system
printf '\nRemoving legacy services\n\n'
systemctl disable SensorCommands
systemctl disable SensorRecording
systemctl stop SensorCommands
systemctl stop SensorRecording
rm -f /etc/systemd/system/SensorCommands.service 2>/dev/null
rm -f /etc/systemd/system/SensorRecording.service 2>/dev/null
systemctl daemon-reload
systemctl enable KootnetSensors 2>/dev/null
