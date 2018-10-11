# Upgrade from Online HTTP server

# HTTP Server Options
HTTP_SERVER="http://kootenay-networks.com"
HTTP_FOLDER="/utils/koot_net_sensors/Installers/raw_files/sensor-rp"

if [ -f "/home/sensors/upgrade/chk_install.sh" ]
then
  bash /home/sensors/upgrade/chk_install.sh
else
  mkdir /home/sensors 2>/dev/null
  wget $HTTP_SERVER$HTTP_FOLDER/upgrade/chk_install.sh -P /home/sensors/
  chmod +x /home/sensors/chk_install.sh
  bash /home/sensors/chk_install.sh
fi
clear
# Download and Upgrade Sensor Programs
mkdir /root/SensorHTTPUpgrade
cd /root/SensorHTTPUpgrade
wget -r -np -nH -R "index.html*" $HTTP_SERVER$HTTP_FOLDER/
cp -R /root/SensorHTTPUpgrade$HTTP_FOLDER/* /home/sensors/
printf '\n\nDownloads Complete\n\n'
# Add easy upgrade, config edits & sensor test app(s) to user pi's home directory
cp /home/sensors/upgrade/update_programs_online.sh /home/pi/update_sensor_online.sh
cp /home/sensors/upgrade/edit_sensor_config.sh /home/pi
cp /home/sensors/upgrade/clean_upgrade_online.sh /home/pi/KootNetSensors/upgrade_online_clean.sh
cp /home/sensors/upgrade/clean_upgrade_smb.sh /home/pi/KootNetSensors/upgrade_smb_clean.sh
# Use Link due to Sensor Test needing modules in the app dir
ln -sf /home/sensors/test_sensors.py /home/pi/test_sensors.py
# Update & Enable Auto Start Applications. Set Wireless Networks. Set File Permissions
bash /home/sensors/upgrade/set_autostart.sh
bash /home/sensors/upgrade/set_permissions.sh
bash /home/sensors/upgrade/set_wifi_networks.sh
# Save datetime to last updated file
date > /home/pi/KootNetSensors/LastUpdated.txt
echo ' Updated with HTTP ' >> /home/pi/KootNetSensors/LastUpdated.txt
printf '\nDone\n\n'
systemctl restart SensorCommands 2>/dev/null
