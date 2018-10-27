# Upgrade from Online HTTP server
# HTTP Server Options
HTTP_SERVER="http://kootenay-networks.com"
HTTP_FOLDER="/utils/koot_net_sensors/Installers/raspbian"
HTTP_ZIP="/KootNetSensors.zip"

if [ -f "/opt/kootnet-sensors/upgrade/chk_install.sh" ]
then
  bash /opt/kootnet-sensors/upgrade/chk_install.sh
else
  rm -f /tmp/chk_install.sh 2>/dev/null
  wget -nd $HTTP_SERVER$HTTP_FOLDER/chk_install.sh -P /tmp/
  bash /tmp/chk_install.sh
fi
clear
# Download and Upgrade Sensor Programs
rm -R /tmp/SensorHTTPUpgrade 2>/dev/null
mkdir /tmp/SensorHTTPUpgrade 2>/dev/null
rm -f /tmp/KootNetSensors.zip 2>/dev/null
printf '\n\nDownloads started\n'
wget $HTTP_SERVER$HTTP_FOLDER$HTTP_ZIP -P /tmp/
printf 'Downloads complete\nUnzipping & installing files\n'
unzip /tmp/KootNetSensors.zip -d /tmp/SensorHTTPUpgrade
cp -f -R /tmp/SensorHTTPUpgrade/sensor-rp/* /opt/kootnet-sensors
cp -f -R /tmp/SensorHTTPUpgrade/sensor-control-center/* /opt/kootnet-control-center
printf 'File install complete\n'
# Add easy upgrade, config edits & sensor test app(s) to user pi's home directory
bash /opt/kootnet-sensors/upgrade/copy_to_home.sh
# Update & Enable Auto Start Applications. Set Wireless Networks. Set File Permissions
bash /opt/kootnet-sensors/upgrade/set_autostart.sh
bash /opt/kootnet-sensors/upgrade/set_permissions.sh
# Save datetime to last updated file
date > /home/pi/KootNetSensors/LastUpdated.txt
echo ' - HTTP ' >> /home/pi/KootNetSensors/LastUpdated.txt
printf '\nDone\n\n'
