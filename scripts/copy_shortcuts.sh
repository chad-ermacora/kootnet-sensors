#!/usr/bin/env bash
if [[ "$1" != "" ]]
then
  USER_NAME=$1
else
  USER_NAME="pi"
fi
mkdir /home/${USER_NAME}/Desktop 2>/dev/null
# Sensor reconfiguration and test shortcut
cat > /usr/share/applications/KootNet-Sensor-Config.desktop << "EOF"
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
chmod 777 /home/${USER_NAME}/Desktop/KootNet*.desktop
