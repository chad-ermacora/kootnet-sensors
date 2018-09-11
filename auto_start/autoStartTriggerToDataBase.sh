sleep 5
echo "$(ps -U root -f | grep "[s]ensorTriggerToDataBase.py")" > /root/tmp34.txt
VARS="$(stat -c "%s" /root/tmp34.txt)"
sleep 1
printf '\nChecking sensorTriggerToDataBase'
if [ "$VARS" -gt "1" ]
then
  printf '\nsensorTriggerToDataBase.py Started\n\n'
else
  python3 /home/sensors/sensorTriggerToDataBase.py &
  printf '\nsensorTriggerToDataBase.py Already Running\n\n'
fi
