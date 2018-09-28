sleep 6
echo "$(ps -U root -f | grep "[S]ensor_Commands.py")" > /root/tmp35.txt
VARS="$(stat -c "%s" /root/tmp35.txt)"
sleep 1
printf '\nChecking Sensor_Commands.py'
if [ "$VARS" -gt "1" ]
then
  printf '\nSensor_Commands.py Already Running\n\n'
else
  python3 /home/sensors/Sensor_Commands.py &
  printf '\nSensor_Commands.py Started\n\n'
fi
