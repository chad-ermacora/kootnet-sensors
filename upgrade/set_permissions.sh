# Make sure permissions are correct
printf '\nSetting permissions\n'
chown pi:pi /home/pi/KootNetSensors -R
chown pi:pi /home/pi/*.sh
chown pi:pi /opt/kootnet-sensors -R
chown pi:pi /opt/kootnet-control-center -R
chmod 754 /home/pi/*.sh 2>/dev/null
chmod 754 /home/pi/*.py 2>/dev/null
chmod 755 /home/pi/KootNetSensors
chmod 664 /home/pi/KootNetSensors/*.txt 2>/dev/null
chmod 754 /home/pi/KootNetSensors/*.sh 2>/dev/null
chmod 755 /home/pi/KootNetSensors/logs
chmod 664 /home/pi/KootNetSensors/logs/* 2>/dev/null
chmod 664 /home/pi/KootNetSensors/data/*.sqlite 2>/dev/null
chmod 755 /opt/kootnet-sensors -R
chmod 754 /opt/kootnet-sensors/*.py 2>/dev/null
chmod 754 /opt/kootnet-sensors/auto_start/*.service 2>/dev/null
chmod 754 /opt/kootnet-sensors/upgrade/*.sh 2>/dev/null
chmod 755 /opt/kootnet-control-center -R
chmod 754 /opt/kootnet-control-center/* 2>/dev/null
chmod 777 /var/log/lighttpd -R 2>/dev/null
