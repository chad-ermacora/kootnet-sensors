clear
printf '\n\nDoing "Clean" Upgrade\nLeaves Database and Config\nDeletes everything else\nRe-Downloads and Installs\n'
rm /home/pi/*.sh 2>/dev/null
rm /home/pi/*.py 2>/dev/null
rm /home/sensors/* 2>/dev/null
rm /home/sensors/auto_start/* 2>/dev/null
rm /home/sensors/sensor_modules/* 2>/dev/null
rm /home/sensors/upgrade/* 2>/dev/null
mount -t cifs //192.168.7.15/Public /mnt/supernas -o username=myself,password='123'
bash /mnt/supernas/RaspberryPi/Sensors/ClientSensors/upgrade/update_programs_smb.sh
bash /mnt/supernas/RaspberryPi/Sensors/ClientSensors/upgrade/update_programs_smb.sh
killall python3
ls -l /home/sensors
printf '\n\nDone\n' 
