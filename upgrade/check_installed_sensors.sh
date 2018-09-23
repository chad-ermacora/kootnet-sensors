# Creates or opens Installed Sensors Configuration File
bash /home/sensors/upgrade/check_folders.sh
if [ -f "/home/pi/KootNetSensors/installed_sensors.txt" ]
then
  printf '\n\nInstalled Sensors File Already Installed\n\n'
else
  printf '\n\Setting up Installed Sensors File\n\n'
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
