# Upgrade from Online HTTP server
# HTTP Server Options
HTTP_SERVER="http://kootenay-networks.com"
HTTP_FOLDER="/utils/koot_net_sensors/Installers/raw_files"

if [ -f "/opt/kootnet-sensors/upgrade/chk_install.sh" ]
then
  bash /opt/kootnet-sensors/upgrade/chk_install.sh
else
  mkdir /opt/kootnet-sensors 2>/dev/null
  wget $HTTP_SERVER$HTTP_FOLDER/upgrade/chk_install.sh -P /opt/kootnet-sensors/
  chmod +x /opt/kootnet-sensors/chk_install.sh
  bash /opt/kootnet-sensors/chk_install.sh
fi
clear
# Download and Upgrade Sensor Programs
mkdir /tmp/SensorHTTPUpgrade
cd /tmp/SensorHTTPUpgrade
printf '\n\nDownloads started\n'
wget -r -np -nH -R "index.html*" $HTTP_SERVER$HTTP_FOLDER/
printf 'Downloads complete\nInstalling files\n'
cp -R /tmp/SensorHTTPUpgrade$HTTP_FOLDER/sensor-rp/* /opt/kootnet-sensors/
cp -R /tmp/SensorHTTPUpgrade$HTTP_FOLDER/sensor-control-center/* /opt/kootnet-control-center/
printf 'File copy complete\n'
# Add easy upgrade, config edits & sensor test app(s) to user pi's home directory
bash /opt/kootnet-sensors/upgrade/copy_to_home.sh
# Update & Enable Auto Start Applications. Set Wireless Networks. Set File Permissions
bash /opt/kootnet-sensors/upgrade/set_autostart.sh
bash /opt/kootnet-sensors/upgrade/set_permissions.sh
# Save datetime to last updated file
date > /home/pi/KootNetSensors/LastUpdated.txt
echo ' Updated with HTTP ' >> /home/pi/KootNetSensors/LastUpdated.txt
printf '\nDone\n\n'
systemctl restart SensorCommands 2>/dev/null
