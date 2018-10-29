printf 'Setting fake-hwclock to run every 1 min in root crontab\n\n'
echo '*/1 * * * * fake-hwclock' >> /tmp/tmp34441.txt
crontab -u root /tmp/tmp34441.txt
rm /tmp/tmp34441.txt
printf 'Recopying, enabling and restarting KootNet sensor services\n'
cp /opt/kootnet-sensors/auto_start/Sensor* /etc/systemd/system
systemctl enable SensorHTTP 2>/dev/null
systemctl enable SensorCommands 2>/dev/null
systemctl enable SensorInterval 2>/dev/null
systemctl enable SensorTrigger 2>/dev/null
systemctl restart SensorHTTP 2>/dev/null
systemctl restart SensorInterval 2>/dev/null
systemctl restart SensorTrigger 2>/dev/null
