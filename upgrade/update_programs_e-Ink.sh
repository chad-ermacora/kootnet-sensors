# Update script that is run when the E-Ink upgrade command is sent
clear
printf 'Starting E-Ink Sensor Upgrade\n'
# Create temporary directories in root and copy things over
rm -R /root/eInkUpgrade 2>/dev/null
mkdir /root/eInkUpgrade 2>/dev/null
cd /root/eInkUpgrade
wget -r -np -nH -R "index.html*" http://192.168.10.5:8009/
cp -R /root/eInkUpgrade/* /home/sensors/
# Update crontab
bash /home/sensors/upgrade/update_crontab.sh
# Add easy upgrade, config edits & sensor test app(s) to user pi's home directory
cp /home/sensors/upgrade/update_programs_online.sh /home/pi/update_sensor_online.sh
cp /home/sensors/upgrade/install_config_sensors.sh /home/pi/sensor_edit_configs.sh
cp /home/sensors/test* /home/pi 2>/dev/null
# Make sure permissions are correct
bash /home/sensors/upgrade/update_file_permissions.sh
# Save datetime to last updated file
date > /home/pi/KootNetSensors/LastUpdated.txt
echo ' Updated with E-Ink Controller ' >> /home/pi/KootNetSensors/LastUpdated.txt
printf '\nDone\n\n'
