# This updates crontab under root, scripts are auto run to keep 3 programs running as well as
# The primary interval sensor program recording to a SQL DB. 
printf 'Configuring root crontab with\n'
printf '1. Sensor_Interval_To_DB.py (Run every 5 min to record to DB)\n'
printf '2. autoStartSensor_Trigger_To_DB.sh (Run every 1 min to start if NOT running)\n'
printf '3. autoStartSensor_Commands.sh (Run every 1 min to start if NOT running)\n'
printf '4. autoStartHTTP.sh (Run every 1 min to start if NOT running)\n'
printf '5. fake-hwclock (Run every 1 min to save current time)\n'
echo '*/5 * * * * python3 /home/sensors/Sensor_Interval_To_DB.py' > /home/pi/tmp34441.txt
echo '*/1 * * * * bash /home/sensors/auto_start/autoStartSensor_Commands.sh' >> /home/pi/tmp34441.txt
echo '*/1 * * * * bash /home/sensors/auto_start/autoStartHTTP.sh' >> /home/pi/tmp34441.txt
echo '*/1 * * * * bash /home/sensors/auto_start/autoStartSensor_Trigger_To_DB.sh' >> /home/pi/tmp34441.txt
echo '*/1 * * * * fake-hwclock' >> /home/pi/tmp34441.txt
crontab -u root /home/pi/tmp34441.txt
rm /home/pi/tmp34441.txt
