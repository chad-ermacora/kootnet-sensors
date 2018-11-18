#!/usr/bin/env bash
USER_DIR="/home/pi/"
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
