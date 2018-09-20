# This will update KootNet Sensor Files over SMB
# In crontab under root, scripts are auto run to keep 3 programs running as well as
# The primary interval sensor program recording to a SQL DB. 
# Later to do -> apparently anything added to cli during run, such as ./script.sh me me2
# Is accessable in the script through $1 $2 etc. 
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
  printf '\nSensors Already Installed, Proceeding with SMB Upgrade\n\n'
else
  bash /home/sensors/upgrade/install_sensors.sh
  printf '\nProceeding with SMB Upgrade\n\n'
fi
# Download and Upgrade Sensor Programs off SMB
printf 'Connecting to SMB and Copying Files\n\n'
mount -t cifs //192.168.7.15/Public /mnt/supernas -o username=myself,password='123'
sleep 1
cp -R /mnt/supernas/RaspberryPi/Sensors/ClientSensors/* /home/sensors
sleep 1
umount /mnt/supernas
# Update crontab
bash /home/sensors/upgrade/update_crontab.sh
# Add easy upgrade, config edits & sensor test app(s) to user pi's home directory
cp /home/sensors/upgrade/update_programs_smb.sh /home/pi/update_sensor_smb.sh
cp /home/sensors/upgrade/install_sensors.sh /home/pi/sensor_edit_configs.sh
cp /home/sensors/test* /home/pi 2>/dev/null
# Make sure permissions are correct
bash /home/sensors/upgrade/update_file_permissions.sh
# Save datetime to last updated file
date > /home/pi/config/LastUpdated.txt
echo ' Updated with SMB ' >> /home/pi/config/LastUpdated.txt
printf '\nDone\n\n'
