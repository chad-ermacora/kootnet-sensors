printf 'Stopping KootNet sensor programs\n\n'
systemctl stop SensorHTTP 2>/dev/null
systemctl stop SensorInterval 2>/dev/null
systemctl stop SensorTrigger 2>/dev/null
printf 'Setting fake-hwclock to run every 1 min in root crontab\n\n'
echo '*/1 * * * * fake-hwclock' >> /tmp/tmp34441.txt
crontab -u root /tmp/tmp34441.txt
rm /tmp/tmp34441.txt
printf 'Re-copying, enabling and starting KootNet sensor services\n'
cp /opt/kootnet-sensors/auto_start/Sensor* /etc/systemd/system
systemctl enable SensorHTTP 2>/dev/null
systemctl enable SensorCommands 2>/dev/null
systemctl enable SensorInterval 2>/dev/null
systemctl enable SensorTrigger 2>/dev/null
systemctl start SensorHTTP 2>/dev/null
systemctl start SensorInterval 2>/dev/null
systemctl start SensorTrigger 2>/dev/null
