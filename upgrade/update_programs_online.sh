# Upgrade from Online HTTP server 
clear
if [ -f "/home/pi/config/zInstalled.txt" ]
then
  printf '\nSensors Already Installed, Proceeding with Online Upgrade\n\n'
else
  bash /home/sensors/upgrade/install_sensors.sh
  printf '\nProceeding with Online Upgrade\n\n'
fi
# Update crontab
bash /home/sensors/upgrade/update_crontab.sh
#  Download and Upgrade Sensor Programs
mkdir /root/SensorHTTPUpgrade
cd /root/SensorHTTPUpgrade
wget -r -np -nH -R "index.html*" http://dragonwarz.net/Stuffz/SensorUpgrades/
cp -R /root/SensorHTTPUpgrade/Stuffz/SensorUpgrades/* /home/sensors/
# Add easy upgrade, config edits & sensor test app(s) to user pi's home directory
cp /home/sensors/upgrade/update_programs_online.sh /home/pi/update_sensor_online.sh
cp /home/sensors/upgrade/install_sensors.sh /home/pi/sensor_edit_configs.sh
cp /home/sensors/test* /home/pi
date > /home/pi/config/LastUpdated.txt
echo ' Updated with HTTP ' >> /home/pi/config/LastUpdated.txt
# Make sure permissions are correct
printf '\n\nSetting Permissions\n' 
chown pi:root /home/pi -R
chown pi:root /home/sensors -R
chmod 754 /home/pi/*.sh
chmod 754 /home/pi/*.py
chmod 644 /home/pi/config/*
chmod 755 /home/sensors -R
chmod 754 /home/sensors/*.py
chmod 754 /home/sensors/auto_start/*.sh
chmod 754 /home/sensors/upgrade/*.sh
chmod 664 /home/sensors/data/*.sqlite 2>/dev/null
chmod 664 /home/sensors/data/Old/* 2>/dev/null
chmod 777 /var/log/lighttpd -R 2>/dev/null
printf '\nDone\n\n'
