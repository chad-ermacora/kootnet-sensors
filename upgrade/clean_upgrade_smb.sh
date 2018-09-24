clear
printf '\n\nDoing "Clean" Upgrade\nLeaves Database and Config\nDeletes everything else\nRe-Downloads and Installs\n'
rm /home/pi/*.sh 2>/dev/null
rm /home/pi/*.py 2>/dev/null
rm /home/sensors/* 2>/dev/null
rm /home/sensors/auto_start/* 2>/dev/null
rm /home/sensors/sensor_modules/* 2>/dev/null
rm /home/sensors/upgrade/* 2>/dev/null
# Connect to and Download Files off SMB Server
mkdir /home/sensors 2>/dev/null
mount -t cifs //192.168.7.15/Public /mnt/supernas -o username=myself,password='123'
cp -R /mnt/supernas/RaspberryPi/Sensors/ClientSensors/* /home/sensors
umount /mnt/supernas
# Run SMB Update script to make sure Folders & Permissions are correct
bash /home/sensors/upgrade/update_programs_smb.sh
killall python3
ls -l /home/sensors
printf '\n\nDone\n' 
