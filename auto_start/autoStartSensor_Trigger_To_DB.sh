sleep 5
echo "$(ps -U root -f | grep "[S]ensor_Trigger_To_DB.py")" > /root/tmp34.txt
VARS="$(stat -c "%s" /root/tmp34.txt)"
sleep 1
printf '\nChecking Sensor_Trigger_To_DB.py'
if [ "$VARS" -gt "1" ]
then
  printf '\nSensor_Trigger_To_DB.py Started\n\n'
else
  python3 /home/sensors/Sensor_Trigger_To_DB.py &
  printf '\nSensor_Trigger_To_DB.py Already Running\n\n'
fi
rm -f /root/tmp34.txt
