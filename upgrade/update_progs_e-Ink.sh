clear
printf 'Starting E-Ink Sensor Upgrade\n'
mkdir /mnt/supernas 2>/dev/null
mkdir /home/sensors 2>/dev/null
mkdir /home/sensors/data 2>/dev/null
mkdir /home/sensors/data/Old 2>/dev/null
printf 'Configuring root crontab with\n'
printf '1. sensorIntervalToDataBase.py (Run every 5 min to record to DB)\n'
printf '2. autoStartTriggerToDataBase.sh (Run every 1 min to start if NOT running)\n'
printf '3. autoStartCommands.sh (Run every 1 min to start if NOT running)\n'
printf '4. autoStartHTTP.sh (Run every 1 min to start if NOT running)\n'
printf '5. fake-hwclock (Run every 1 min to save current time to file loads file on boot)\n'
echo '*/5 * * * * python3 /home/sensors/sensorIntervalToDataBase.py' > /home/pi/tmp34441.txt
echo '*/1 * * * * bash /home/sensors/auto_start/autoStartCommands.sh' >> /home/pi/tmp34441.txt
echo '*/1 * * * * bash /home/sensors/auto_start/autoStartHTTP.sh' >> /home/pi/tmp34441.txt
echo '*/1 * * * * bash /home/sensors/auto_start/autoStartTriggerToDataBase.sh' >> /home/pi/tmp34441.txt
echo '*/1 * * * * fake-hwclock' >> /home/pi/tmp34441.txt
crontab -u root /home/pi/tmp34441.txt
mkdir /root/httpUpgrade
cd /root/httpUpgrade
curl -G http://192.168.10.5:8009/sensorCommands.py --output /home/sensors/sensorCommands.py
wget -r -np -nH -R "index.html*" http://192.168.10.5:8009/
mv -f /root/httpUpgrade/* /home/sensors/
chown pi:root /home/sensors -R
chmod 755 /home/sensors -R
chmod 664 /home/sensors/data/*.sqlite 2>/dev/null
chmod 754 /home/sensors/*.py
chmod 754 /home/sensors/upgrade/*.sh
cp /home/sensors/upgrade/install_update_sensor_nas.sh /home/pi/update_sensor_nas.sh
chmod 754 /home/pi/*.sh
rm /home/pi/tmp34441.txt
date > /home/pi/config/LastUpdated.txt
echo ' Updated with E-Ink Controller ' >> /home/pi/config/LastUpdated.txt
printf 'done\n'
