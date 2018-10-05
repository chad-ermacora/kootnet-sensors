printf 'Stopping KootNet Sensor Programs\n\n'
sudo systemctl stop SensorHTTP 2>/dev/null
sudo systemctl stop SensorCommands 2>/dev/null
sudo systemctl stop SensorInterval 2>/dev/null
sudo systemctl stop SensorTrigger 2>/dev/null
printf 'Setting fake-hwclock to run every 1 min in root crontab\n\n'
echo '*/1 * * * * fake-hwclock' >> /home/pi/tmp34441.txt
crontab -u root /home/pi/tmp34441.txt
rm /home/pi/tmp34441.txt
printf 'Copying KootNet Sensor Service Files\n\n'
cp /home/sensors/auto_start/Sensor* /etc/systemd/system
printf 'Re-loading, enabling and starting KootNet Sensor Services\n\n'
sudo systemctl daemon-reload 2>/dev/null
sudo systemctl enable SensorHTTP 2>/dev/null
sudo systemctl enable SensorCommands 2>/dev/null
sudo systemctl enable SensorInterval 2>/dev/null
sudo systemctl enable SensorTrigger 2>/dev/null
sudo systemctl start SensorHTTP 2>/dev/null
sudo systemctl start SensorCommands 2>/dev/null
sudo systemctl start SensorInterval 2>/dev/null
sudo systemctl start SensorTrigger 2>/dev/null
