# This will update KootNet Sensor Files over SMB
# Change SMB to match your windows share & Login
# Make sure SMB_FOLDER points to the root directory holding the Sensor Upgrade Files

# SMB Options
SMB_SERVER="//gamercube1"
SMB_FOLDER="/sensor-rp"
CIFS_OPTIONS="username=myself,password='123'"

clear
if [ -f "/home/sensors/upgrade/chk_install.sh" ]
then
  bash /home/sensors/upgrade/chk_install.sh
else
  mkdir /home/sensors 2>/dev/null
  mkdir /mnt/supernas 2>/dev/null
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
rm /home/pi//KootNetSensors/*.sh* 2>/dev/null
rm /home/pi/KootNetSensors/*.py* 2>/dev/null
rm /home/pi/*.sh* 2>/dev/null
rm /home/pi/*.py* 2>/dev/null
# Add easy upgrade, config edits & sensor test app(s) to user pi's home directory
bash /home/sensors/upgrade/copy_to_home.sh
# Update & Enable Auto Start Applications. Set Wireless Networks. Set File Permissions
bash /home/sensors/upgrade/set_autostart.sh
bash /home/sensors/upgrade/set_wifi_networks.sh
bash /home/sensors/upgrade/set_permissions.sh
# Save datetime to last updated file
date > /home/pi/KootNetSensors/LastUpdated.txt
echo ' Updated with SMB ' >> /home/pi/KootNetSensors/LastUpdated.txt
printf '\nDone\n\n'
systemctl restart SensorCommands 2>/dev/null
