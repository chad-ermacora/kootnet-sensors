# This will update KootNet Sensor Files over SMB
# Change SMB to match your windows share & Login
# Make sure SMB_FOLDER points to the root directory holding the Sensor Upgrade Files

# SMB Options
SMB_SERVER="//192.168.10.7"
SMB_FOLDER="/sensor-rp"
CIFS_OPTIONS="username=myself,password='123'"
CIFS_MOUNT="/mnt/supernas"

mkdir $CIFS_MOUNT
clear
bash /home/sensors/upgrade/check_installed_sensors.sh
if [ -f "/home/pi/KootNetSensors/zInstalled.txt" ]
then
  printf '\nSensors Already Installed, Proceeding with SMB Upgrade\n\n'
else
  bash /home/sensors/upgrade/install_kootnet_sensors.sh
  printf '\nProceeding with SMB Upgrade\n\n'
fi
# Download and Upgrade Sensor Programs off SMB
printf 'Connecting to SMB and Copying Files\n\n'
mount -t cifs $SMB_SERVER$SMB_FOLDER $CIFS_MOUNT -o $CIFS_OPTIONS
sleep 1
cp -R $CIFS_MOUNT/* /home/sensors
sleep 1
umount $CIFS_MOUNT
sleep 1
# Update & Enable Auto Start Applications
bash /home/sensors/upgrade/update_autostart.sh
# Add easy upgrade, config edits & sensor test app(s) to user pi's home directory
cp /home/sensors/upgrade/update_programs_smb.sh /home/pi/update_sensor_smb.sh
cp /home/sensors/upgrade/install_kootnet_sensors.sh /home/pi/config_edit.sh
cp /home/sensors/upgrade/clean_upgrade_online.sh /home/pi/KootNetSensors/upgrade_online_clean.sh
cp /home/sensors/upgrade/clean_upgrade_smb.sh /home/pi/KootNetSensors/upgrade_smb_clean.sh
ln -sf /home/sensors/test_sensors.py /home/pi/test_sensors.py
# Make sure permissions are correct
bash /home/sensors/upgrade/update_file_permissions.sh
# Save datetime to last updated file
date > /home/pi/KootNetSensors/LastUpdated.txt
echo ' Updated with SMB ' >> /home/pi/KootNetSensors/LastUpdated.txt
printf '\nDone\n\n'
systemctl restart SensorCommands 2>/dev/null
