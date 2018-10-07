# This will update KootNet Sensor Files over SMB
# Change SMB to match your windows share & Login
# Make sure SMB_FOLDER points to the root directory holding the Sensor Upgrade Files

# SMB Options
SMB_SERVER="//192.168.10.7"
SMB_FOLDER="/sensor-rp"
CIFS_OPTIONS="username=myself,password='123'"

clear
if [ -f "/home/sensors/upgrade/chk_install.sh" ]
then
  bash /home/sensors/upgrade/chk_install.sh
else
  mkdir /home/sensors 2>/dev/null
  mkdir /home/supernas 2>/dev/null
  mount -t cifs $SMB_SERVER$SMB_FOLDER /mnt/supernas -o $CIFS_OPTIONS
  sleep 1
  bash /mnt/supernas/upgrade/chk_install.sh
  sleep 1
  umount /mnt/supernas
  sleep 1
  printf '\nProceeding with SMB Upgrade\n\n'
fi
# Download and Upgrade Sensor Programs off SMB
printf 'Connecting to SMB and Copying Files\n\n'
mount -t cifs $SMB_SERVER$SMB_FOLDER /mnt/supernas -o $CIFS_OPTIONS
sleep 1
cp -R /mnt/supernas/* /home/sensors
sleep 1
umount /mnt/supernas
sleep 1
# Remove legacy files
rm /home/pi/KootNetSensors/clean_upgrade_online.sh 2>/dev/null
rm /home/pi/KootNetSensors/clean_upgrade_smb.sh 2>/dev/null
rm /home/pi/KootNetSensors/sensor_type.txt 2>/dev/null
# Add easy upgrade, config edits & sensor test app(s) to user pi's home directory
cp /home/sensors/upgrade/update_programs_smb.sh /home/pi/update_sensor_smb.sh
cp /home/sensors/upgrade/edit_sensor_config.sh /home/pi
cp /home/sensors/upgrade/clean_upgrade_online.sh /home/pi/KootNetSensors/upgrade_online_clean.sh
cp /home/sensors/upgrade/clean_upgrade_smb.sh /home/pi/KootNetSensors/upgrade_smb_clean.sh
cp -f /home/sensors/test_sensors.py /home/pi
# Update & Enable Auto Start Applications. Set Wireless Networks. Set File Permissions
bash /home/sensors/upgrade/set_autostart.sh
bash /home/sensors/upgrade/set_wifi_networks.sh
bash /home/sensors/upgrade/set_permissions.sh
# Save datetime to last updated file
date > /home/pi/KootNetSensors/LastUpdated.txt
echo ' Updated with SMB ' >> /home/pi/KootNetSensors/LastUpdated.txt
printf '\nDone\n\n'
systemctl restart SensorCommands 2>/dev/null
