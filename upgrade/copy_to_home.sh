# Add easy upgrade, config edits & sensor test app(s) to user pi's home directory
cp /home/sensors/upgrade/update_programs_smb.sh /home/pi/update_sensor_smb.sh
cp /home/sensors/upgrade/edit_sensor_config.sh /home/pi/edit_sensor_config.sh
cp /home/sensors/upgrade/clean_upgrade_online.sh /home/pi/KootNetSensors/upgrade_online_clean.sh
cp /home/sensors/upgrade/clean_upgrade_smb.sh /home/pi/KootNetSensors/upgrade_smb_clean.sh
# Use Link due to Sensor Test needing modules in the app dir
ln -sf /home/sensors/test_sensors.py /home/pi/test_sensors.py
