#!/usr/bin/env bash
# Sensor reconfiguration and test shortcut
cat > /usr/share/applications/KootNet-Sensor-Config.desktop << "EOF"
[Desktop Entry]
Name=Kootnet Sensors - CLI Configuration & Test
Comment=Reconfigure sensor & display sensor readings
Icon=/usr/share/icons/PiX/128x128/mimetypes/shellscript.png
Exec=/bin/bash /opt/kootnet-sensors/scripts/edit_sensor_config.sh
Type=Application
Encoding=UTF-8
Terminal=true
Categories=Utility;Science;
EOF
cat > /usr/share/applications/KootNet-Sensor-Web-Config.desktop << "EOF"
[Desktop Entry]
Name=Kootnet Sensors - Web Configuration
Comment=Web interface for configuring sensor
Type=Application
Icon=/opt/kootnet-sensors/extras/icon.ico
TryExec=/usr/bin/x-www-browser
Exec=x-www-browser http://localhost:10065/SystemCommands
Terminal=false
Categories=Utility;Science;
StartupNotify=true
EOF
