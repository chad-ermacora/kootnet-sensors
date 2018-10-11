# Update script that is run when the E-Ink upgrade command is sent
EINK_HTTP_URL='http://192.168.10.5:8009'

clear
printf 'Starting E-Ink Sensor Upgrade\n'
# Create temporary directories in root and copy things over
rm -R /root/eInkUpgrade 2>/dev/null
mkdir /root/eInkUpgrade 2>/dev/null
cd /root/eInkUpgrade
wget -r -np -nH -R "index.html*" $EINK_HTTP_URL/
cp -R /root/eInkUpgrade/* /home/sensors/
# Add easy upgrade, config edits & sensor test app(s) to user pi's home directory
cp /home/sensors/upgrade/update_programs_online.sh /home/pi/update_sensor_online.sh
cp /home/sensors/upgrade/edit_sensor_config.sh /home/pi
cp /home/sensors/upgrade/clean_upgrade_online.sh /home/pi/KootNetSensors/upgrade_online_clean.sh
cp /home/sensors/upgrade/clean_upgrade_smb.sh /home/pi/KootNetSensors/upgrade_smb_clean.sh
# Use Link due to Sensor Test needing modules in the app dir
ln -sf /home/sensors/test_sensors.py /home/pi/test_sensors.py
# Update & Enable Auto Start Applications. Set Wireless Networks. Set File Permissions
bash /home/sensors/upgrade/set_autostart.sh
bash /home/sensors/upgrade/set_wifi_networks.sh
bash /home/sensors/upgrade/set_permissions.sh
# Save datetime to last updated file
date > /home/pi/KootNetSensors/LastUpdated.txt
echo ' Updated with E-Ink Controller ' >> /home/pi/KootNetSensors/LastUpdated.txt
printf '\nDone\n\n'
systemctl restart SensorCommands 2>/dev/null
