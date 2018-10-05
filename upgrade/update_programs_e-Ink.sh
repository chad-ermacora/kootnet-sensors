# Update script that is run when the E-Ink upgrade command is sent
clear
printf 'Starting E-Ink Sensor Upgrade\n'
# Create temporary directories in root and copy things over
rm -R /root/eInkUpgrade 2>/dev/null
mkdir /root/eInkUpgrade 2>/dev/null
cd /root/eInkUpgrade
wget -r -np -nH -R "index.html*" http://192.168.10.5:8009/
cp -R /root/eInkUpgrade/* /home/sensors/
# Update Auto Start Applications
bash /home/sensors/upgrade/update_autostart.sh
# Add easy upgrade, config edits & sensor test app(s) to user pi's home directory
cp /home/sensors/upgrade/update_programs_online.sh /home/pi/update_sensor_online.sh
cp /home/sensors/upgrade/install_kootnet_sensors.sh /home/pi/config_edit.sh
ln -sf /home/sensors/test_sensors.py /home/pi/test_sensors.py
# Make sure permissions are correct
bash /home/sensors/upgrade/update_file_permissions.sh
# Save datetime to last updated file
date > /home/pi/KootNetSensors/LastUpdated.txt
echo ' Updated with E-Ink Controller ' >> /home/pi/KootNetSensors/LastUpdated.txt
printf '\nDone\n\n'
