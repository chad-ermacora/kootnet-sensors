# This will update KootNet Sensor Files over SMB, change options to match your windows share
# Make sure SMB_SHARE points to the root share holding both Sensor & Control Center folders
SMB_SERVER="//gamercube1"
SMB_SHARE="/PyCharmProjects"
SMB_SENSOR="/sensor-rp"
SMB_CONTROL_CENTER="/sensor-control-center"
CIFS_OPTIONS="username=myself,password='123'"
RSYNC_EXCLUDE="--exclude .git --exclude .idea --exclude __pycache__ --exclude test_files/SensorIntervalGraph.html --exclude test_files/SensorTriggerGraph.html"

clear
if [ -f "/opt/kootnet-sensors/upgrade/chk_install.sh" ]
then
  bash /opt/kootnet-sensors/upgrade/chk_install.sh
else
  mkdir /mnt/supernas 2>/dev/null
  mount -t cifs $SMB_SERVER$SMB_SHARE /mnt/supernas -o $CIFS_OPTIONS
  sleep 1
  bash /mnt/supernas/sensor-rp/upgrade/chk_install.sh
  umount /mnt/supernas
  printf '\nProceeding with SMB upgrade\n'
fi
# Download and Upgrade Sensor Programs off SMB
printf '\nConnecting to SMB & copying files\n'
mount -t cifs $SMB_SERVER$SMB_SHARE /mnt/supernas -o $CIFS_OPTIONS
sleep 1
printf 'Copying sensor files\n'
rsync -q -r -4 -P /mnt/supernas$SMB_SENSOR/ /opt/kootnet-sensors/ $RSYNC_EXCLUDE
printf 'Copying control center files\n\n'
rsync -q -r -4 -P /mnt/supernas$SMB_CONTROL_CENTER/ /opt/kootnet-control-center/ $RSYNC_EXCLUDE
sleep 1
umount /mnt/supernas
# Remove legacy files
rm /home/pi/KootNetSensors/sensor_type.txt 2>/dev/null
rm /home/pi/KootNetSensors/*.sh* 2>/dev/null
rm /home/pi/KootNetSensors/*.py* 2>/dev/null
rm /home/pi/*.sh* 2>/dev/null
rm /home/pi/*.py* 2>/dev/null
# Add easy upgrade, config edits & sensor test app(s) to user pi's home directory
bash /opt/kootnet-sensors/upgrade/copy_to_home.sh
# Update & Enable Auto Start Applications. Set Wireless Networks. Set File Permissions
bash /opt/kootnet-sensors/upgrade/set_autostart.sh
bash /opt/kootnet-sensors/upgrade/set_permissions.sh
# Save datetime to last updated file
date > /home/pi/KootNetSensors/LastUpdated.txt
echo ' - SMB' >> /home/pi/KootNetSensors/LastUpdated.txt
printf '\nDone\n\n'
