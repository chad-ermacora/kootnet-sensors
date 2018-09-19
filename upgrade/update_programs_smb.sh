# This will update KootNet Sensor Files over SMB
# In crontab under root, scripts are auto run to keep 3 programs running as well as
# The primary interval sensor program recording to a SQL DB. 
# Later to do -> apparently anything added to cli during run, such as ./script.sh me me2
# Is accessable in the script through $1 $2 etc. 
clear
if [ -f "/home/pi/config/zInstalled.txt" ]
then
  printf '\nSensors Already Installed, Proceeding with SMB Upgrade\n\n'
else
  bash /home/sensors/upgrade/install_sensors.sh
  printf '\nProceeding with SMB Upgrade\n\n'
fi
# Update crontab
bash /home/sensors/upgrade/update_crontab.sh
# Download and Upgrade Sensor Programs off SMB
printf 'Connecting to SMB and Copying Files\n\n'
mount -t cifs //192.168.7.15/Public /mnt/supernas -o username=myself,password='123'
sleep 1
cp -R /mnt/supernas/RaspberryPi/Sensors/ClientSensors/* /home/sensors
# Add easy upgrade, config edits & sensor test app(s) to user pi's home directory
cp /home/sensors/upgrade/update_programs_smb.sh /home/pi/update_sensor_smb.sh
cp /home/sensors/upgrade/install_sensors.sh /home/pi/sensor_edit_configs.sh
cp /home/sensors/test* /home/pi
umount /mnt/supernas
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
date > /home/pi/config/LastUpdated.txt
echo ' Updated with SMB ' >> /home/pi/config/LastUpdated.txt
