# Upgrade from Online HTTP server 
clear
bash /home/sensors/upgrade/check_folders.sh
bash /home/sensors/upgrade/check_installed_sensors.sh
if [ -f "/home/pi/KootNetSensors/zInstalled.txt" ]
then
  printf '\nSensors Already Installed, Proceeding with Online Upgrade\n\n'
else
  bash /home/sensors/upgrade/install_config_sensors.sh
  printf '\nProceeding with Online Upgrade\n\n'
fi
#  Download and Upgrade Sensor Programs
mkdir /root/SensorHTTPUpgrade
cd /root/SensorHTTPUpgrade
wget -r -np -nH -R "index.html*" http://kootenay-networks.com/utils/koot_net_sensors/Installers/raw_files/sensor-rp/
cp -R /root/SensorHTTPUpgrade/utils/koot_net_sensors/Installers/raw_files/sensor-rp/* /home/sensors/
printf '\n\nDownloads Complete\n\n'
# Update crontab
bash /home/sensors/upgrade/update_crontab.sh
# Add easy upgrade, config edits & sensor test app(s) to user pi's home directory
cp /home/sensors/upgrade/update_programs_online.sh /home/pi/update_sensor_online.sh
cp /home/sensors/upgrade/install_config_sensors.sh /home/pi/sensor_edit_configs.sh
cp /home/sensors/upgrade/clean_upgrade.sh /home/pi/KootNetSensors/clean_upgrade.sh
cp /home/sensors/test* /home/pi 2>/dev/null
# Make sure permissions are correct
bash /home/sensors/upgrade/update_file_permissions.sh
# Save datetime to last updated file
date > /home/pi/KootNetSensors/LastUpdated.txt
echo ' Updated with HTTP ' >> /home/pi/KootNetSensors/LastUpdated.txt
printf '\nDone\n\n'
