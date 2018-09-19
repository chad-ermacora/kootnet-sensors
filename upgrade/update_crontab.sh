# This updates crontab under root, scripts are auto run to keep 3 programs running as well as
# The primary interval sensor program recording to a SQL DB. 
clear
printf 'Configuring root crontab with\n'
printf '1. sensorIntervalToDataBase.py (Run every 5 min to record to DB)\n'
printf '2. autoStartTriggerToDataBase.sh (Run every 1 min to start if NOT running)\n'
printf '3. autoStartServerCommands.sh (Run every 1 min to start if NOT running)\n'
printf '4. autoStartHTTP.sh (Run every 1 min to start if NOT running)\n'
printf '5. fake-hwclock (Run every 1 min to save current time to file loads file on boot)\n'
echo '*/5 * * * * python3 /home/sensors/sensorIntervalToDataBase.py' > /home/pi/tmp34441.txt
echo '*/1 * * * * bash /home/sensors/auto_start/autoStartServerCommands.sh' >> /home/pi/tmp34441.txt
echo '*/1 * * * * bash /home/sensors/auto_start/autoStartHTTP.sh' >> /home/pi/tmp34441.txt
echo '*/1 * * * * bash /home/sensors/auto_start/autoStartTriggerToDataBase.sh' >> /home/pi/tmp34441.txt
echo '*/1 * * * * fake-hwclock' >> /home/pi/tmp34441.txt
crontab -u root /home/pi/tmp34441.txt
rm /home/pi/tmp34441.txt
