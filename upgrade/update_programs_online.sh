# Upgrade from Online HTTP server

# HTTP Server Options
HTTP_SERVER="http://kootenay-networks.com"
HTTP_FOLDER="/utils/koot_net_sensors/Installers/raw_files/sensor-rp"

clear
bash /home/sensors/upgrade/check_installed_sensors.sh 2>/dev/null
if [ -f "/home/pi/KootNetSensors/zInstalled.txt" ]
then
  printf '\nSensors Already Installed, Proceeding with Online Upgrade\n\n'
else
  bash /home/sensors/upgrade/install_kootnet_sensors.sh
  printf '\nProceeding with Online Upgrade\n\n'
fi
# Download and Upgrade Sensor Programs
mkdir /root/SensorHTTPUpgrade
cd /root/SensorHTTPUpgrade
wget -r -np -nH -R "index.html*" $HTTP_SERVER$HTTP_FOLDER/
cp -R /root/SensorHTTPUpgrade$HTTP_FOLDER/* /home/sensors/
printf '\n\nDownloads Complete\n\n'
# Update & Enable Auto Start Applications
bash /home/sensors/upgrade/update_autostart.sh
# Add easy upgrade, config edits & sensor test app(s) to user pi's home directory
cp /home/sensors/upgrade/update_programs_online.sh /home/pi/update_sensor_online.sh
cp /home/sensors/upgrade/install_kootnet_sensors.sh /home/pi/config_edit.sh
cp /home/sensors/upgrade/clean_upgrade_online.sh /home/pi/KootNetSensors/upgrade_online_clean.sh
cp /home/sensors/upgrade/clean_upgrade_smb.sh /home/pi/KootNetSensors/upgrade_smb_clean.sh
ln -sf /home/sensors/test_sensors.py /home/pi/test_sensors.py
# Make sure permissions are correct
bash /home/sensors/upgrade/update_file_permissions.sh
# Save datetime to last updated file
date > /home/pi/KootNetSensors/LastUpdated.txt
echo ' Updated with HTTP ' >> /home/pi/KootNetSensors/LastUpdated.txt
printf '\nDone\n\n'
systemctl restart SensorCommands 2>/dev/null
