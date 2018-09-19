# Update script that is run when the E-Ink upgrade command is sent
clear
printf 'Starting E-Ink Sensor Upgrade\n'
# Update crontab
bash /home/sensors/upgrade/update_crontab.sh
# Create temporary directories in root and copy things over
rm -R /root/eInkUpgrade 2>/dev/null
mkdir /root/eInkUpgrade 2>/dev/null
cd /root/eInkUpgrade
wget -r -np -nH -R "index.html*" http://192.168.10.5:8009/
cp -R /root/eInkUpgrade/* /home/sensors/
# Add easy upgrade, config edits & sensor test app(s) to user pi's home directory
cp /home/sensors/upgrade/update_programs_online.sh /home/pi/update_sensor_online.sh
cp /home/sensors/upgrade/install_sensors.sh /home/pi/sensor_edit_configs.sh
cp /home/sensors/test* /home/pi
date > /home/pi/config/LastUpdated.txt
echo ' Updated with E-Ink Controller ' >> /home/pi/config/LastUpdated.txt
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
