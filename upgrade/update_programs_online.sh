# Upgrade from Online HTTP server 
clear
if [ -f "/home/pi/config/sensor_type.txt" ]
then
  printf '\n'
else
  printf '\nInstalling Sensor Type Config'
  mkdir /home/pi/config 2>/dev/null
  cat > /home/pi/config/sensor_type.txt << "EOF"
Change the number in front of each line. Enable = 1 & Disable = 0
1 = RP_system
0 = RP_senseHAT
0 = Pimoroni_bh1745
0 = Pimoroni_BME680
0 = Pimoroni_Enviro
0 = Pimoroni_LSM303D
0 = Pimoroni_VL53L1X
EOF
  nano /home/pi/config/sensor_type.txt
fi
if [ -f "/home/pi/config/zInstalled.txt" ]
then
  printf '\nSensors Already Installed, Proceeding with Online Upgrade\n\n'
else
  bash /home/sensors/upgrade/install_sensors.sh
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
cp /home/sensors/upgrade/install_sensors.sh /home/pi/sensor_edit_configs.sh
cp /home/sensors/test* /home/pi 2>/dev/null
# Make sure permissions are correct
bash /home/sensors/upgrade/update_file_permissions.sh
# Save datetime to last updated file
date > /home/pi/config/LastUpdated.txt
echo ' Updated with HTTP ' >> /home/pi/config/LastUpdated.txt
printf '\nDone\n\n'
