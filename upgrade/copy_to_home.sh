# Add easy upgrade, config edits & sensor test app(s) to user pi's home directory
cp -f /opt/kootnet-sensors/upgrade/update_programs_smb.sh /home/pi/update_sensors_smb.sh
cp -f /opt/kootnet-sensors/upgrade/update_programs_online.sh /home/pi/update_sensors_online.sh
cp -f /opt/kootnet-sensors/upgrade/clean_upgrade_online.sh /home/pi/KootNetSensors/upgrade_online_clean.sh
cp -f /opt/kootnet-sensors/upgrade/clean_upgrade_smb.sh /home/pi/KootNetSensors/upgrade_smb_clean.sh
cp -f /opt/kootnet-sensors/upgrade/uninstall.sh /home/pi/KootNetSensors/zUninstall.sh
ln -sf /opt/kootnet-sensors/upgrade/edit_sensor_config.sh /home/pi/edit_sensor_config.sh
# Use Link due to Sensor Test needing modules in the app dir
ln -sf /opt/kootnet-sensors/test_sensors.py /home/pi/test_sensors.py
ln -sf /opt/kootnet-control-center/main_guizero.py /home/pi/control-center.py
cat > /home/pi/Desktop/KootNet-Control-Center.desktop << "EOF"
[Desktop Entry]
Name=Sensors - Control Center
Comment=Monitor and Manage KootNet Sensors
Icon=/opt/kootnet-control-center/additional_files/icon.ico
Exec=/usr/bin/python3 /opt/kootnet-control-center/main_guizero.py
Type=Application
Encoding=UTF-8
Terminal=false
Categories=None;
EOF
