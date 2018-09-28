sleep 2
echo "$(ps -U root -f | grep "[S]ensor_Interval_To_DB.py")" > /root/tmp354.txt
VARS="$(stat -c "%s" /root/tmp354.txt)"
sleep 1
printf '\nChecking Sensor_Interval_To_DB.py'
if [ "$VARS" -gt "1" ]
then
  printf '\nSensor_Interval_To_DB.py Started\n\n'
else
  python3 /home/sensors/Sensor_Interval_To_DB.py &
  printf '\nSensor_Interval_To_DB.py Already Running\n\n'
fi
rm -f /root/tmp354.txt
