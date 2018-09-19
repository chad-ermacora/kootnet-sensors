sleep 4
echo "$(ps -U root -f | grep "[s]ensorServerCommands.py")" > /root/tmp35.txt
VARS="$(stat -c "%s" /root/tmp35.txt)"
sleep 1
printf '\nChecking sensorServerCommands.py'
if [ "$VARS" -gt "1" ]
then
  printf '\nsensorServerCommands.py Already Running\n\n'
else
  python3 /home/sensors/sensorServerCommands.py &
  printf '\nsensorServerCommands.py Started\n\n'
fi
