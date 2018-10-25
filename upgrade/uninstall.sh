# This script will remove all Sensor and Control Center program files off the Sensor, leaving configuration and data
printf '\nDisabling & stopping all sensor services\n'
systemctl disable SensorHTTP
systemctl disable SensorCommands
systemctl disable SensorInterval
systemctl disable SensorTrigger
systemctl stop SensorHTTP
systemctl stop SensorCommands
systemctl stop SensorInterval
systemctl stop SensorTrigger
printf '\nRemoving sensor service files\n'
rm -f /etc/systemd/system/SensorCommands.service 2>/dev/null
rm -f /etc/systemd/system/SensorHTTP.service 2>/dev/null
rm -f /etc/systemd/system/SensorInterval.service 2>/dev/null
rm -f /etc/systemd/system/SensorTrigger.service 2>/dev/null
# Restore /etc/network/interfaces & /etc/wpa_supplicant/wpa_supplicant.conf
if [ -f "/home/pi/KootNetSensors/backups/interfaces" ]
then
  printf '\nRestoring original /etc/network/interfaces\n'
  cp -f /home/pi/KootNetSensors/backups/interfaces /etc/network/interfaces 2>/dev/null
fi
if [ -f "/home/pi/KootNetSensors/backups/wpa_supplicant.conf" ]
then
  printf 'Restoring original /etc/wpa_supplicant/wpa_supplicant.conf\n'
  cp -f /home/pi/KootNetSensors/backups/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf 2>/dev/null
fi
printf '\nRemoving all Sensor & Control Center program files\n'
# Remove Sensor & Control Center program directories
killall python3 2>/dev/null
rm -f -R /opt/kootnet-sensors
rm -f -R /opt/kootnet-control-center
# Remove Shortcuts and easy access copies
rm -f /home/pi/Desktop/KootNet-Control-Center.desktop 2>/dev/null
rm -f /home/pi/control-center.py 2>/dev/null
rm -f /home/pi/test_sensors.py 2>/dev/null
rm -f /home/pi/edit_sensor_config.sh 2>/dev/null
rm -f /home/pi/update_sensor_smb.sh 2>/dev/null
rm -f /home/pi/KootNetSensors/upgrade_smb_clean.sh 2>/dev/null
rm -f /home/pi/KootNetSensors/upgrade_online_clean.sh 2>/dev/null
rm -f /home/pi/update_sensors_smb.sh 2>/dev/null
rm -f /home/pi/update_sensors_online.sh 2>/dev/null
# Remove install check files
rm -f /home/pi/KootNetSensors/zInstalled.txt 2>/dev/null
rm -f /home/pi/KootNetSensors/installed_sensors.txt 2>/dev/null
# Remove Misc. other
crontab -r
printf '\n\nUninstall complete\n'
rm -f /home/pi/KootNetSensors/zUninstall.sh
