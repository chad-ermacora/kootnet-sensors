# Creates or opens Installed Sensors Configuration File
bash /home/sensors/upgrade/check_folders.sh
killall nano 2>/dev/null
if [ -f "/home/pi/KootNetSensors/installed_sensors.txt" ]
then
  printf '\nInstalled Sensors File Already Installed\n'
else
  printf '\nSetting up Installed Sensors File\n'
  cat > /home/pi/KootNetSensors/installed_sensors.txt << "EOF"
Change the number in front of each line. Enable = 1 & Disable = 0
1 = RP_system
0 = RP_senseHAT
0 = Pimoroni_bh1745
0 = Pimoroni_BME680
0 = Pimoroni_Enviro
0 = Pimoroni_LSM303D
0 = Pimoroni_VL53L1X
EOF
  nano /home/pi/KootNetSensors/installed_sensors.txt
fi
if [ -f "/home/pi/KootNetSensors/config.txt" ]
then
  printf '\nConfig File Already Installed\n'
else
  printf '\nSetting up Config File\n'
  cat > /home/pi/KootNetSensors/config.txt << "EOF"
Enable = 1 & Disable = 0
1 = Record Sensors to SQL Database
300 = Duration between Interval readings in Seconds
0.15 = Duration between Trigger readings in Seconds
0 = Enable Custom Settings
0.0 = Custom Accelerometer variance
0.0 = Custom Magnetometer variance
0.0 = Custom Gyroscope variance
EOF
  nano /home/pi/KootNetSensors/config.txt
fi
