#!/usr/bin/env bash
USER_DIR="/home/pi"
mkdir /home/pi/Desktop 2>/dev/null
# Sensor reconfiguration and test shortcut
cat > ${USER_DIR}/Desktop/KootNet-Sensor-Config.desktop << "EOF"
[Desktop Entry]
Name=Kootnet Sensors - Configuration & Test
Comment=Reconfigure sensor & display sensor readings
Icon=/usr/share/icons/PiX/128x128/mimetypes/shellscript.png
Exec=/bin/bash /opt/kootnet-sensors/scripts/edit_sensor_config.sh
Type=Application
Encoding=UTF-8
Terminal=true
Categories=Utility;Science;
EOF
cp -f ${USER_DIR}/Desktop/KootNet-Sensor-Config.desktop /usr/share/applications/KootNet-Sensor-Config.desktop
# Sensor Control Center shortcut
cat > ${USER_DIR}/Desktop/KootNet-Control-Center.desktop << "EOF"
[Desktop Entry]
Name=Kootnet Sensors - Control Center
Comment=Monitor and Manage KootNet Sensors
Icon=/opt/kootnet-control-center/additional_files/icon.ico
Exec=/home/kootnet_data/python-env/bin/python /opt/kootnet-control-center/start_app_guizero.py
Type=Application
Encoding=UTF-8
Terminal=false
Categories=Utility;Science;
EOF
cp -f ${USER_DIR}/Desktop/KootNet-Control-Center.desktop /usr/share/applications/KootNet-Control-Center.desktop
