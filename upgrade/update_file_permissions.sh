# Make sure permissions are correct
printf '\n\nSetting Permissions\n' 
chown pi:root /home/pi -R
chown pi:root /home/sensors -R
chmod 754 /home/pi/*.sh 2>/dev/null
chmod 754 /home/pi/*.py 2>/dev/null
chmod 755 /home/pi/config
chmod 664 /home/pi/config/* 2>/dev/null
chmod 755 /home/pi/config/logs
chmod 664 /home/pi/config/logs/* 2>/dev/null
chmod 755 /home/sensors -R
chmod 754 /home/sensors/*.py 2>/dev/null
chmod 754 /home/sensors/auto_start/*.sh 2>/dev/null
chmod 754 /home/sensors/upgrade/*.sh 2>/dev/null
chmod 664 /home/sensors/data/*.sqlite 2>/dev/null
chmod 664 /home/sensors/data/Old/* 2>/dev/null
chmod 777 /var/log/lighttpd -R
