sleep 3
echo "$(ps -U pi -f | grep "[l]ighttpd")" > /root/tmp31.txt
VARS="$(stat -c "%s" /root/tmp31.txt)"
sleep 1
printf '\nChecking HTTP Server'
if [ "$VARS" -gt "1" ]
then
  printf '\n\nHTTP Already Running\n\n'
else
  /usr/sbin/lighttpd -f /home/sensors/lighttpd.conf
  printf '\n\nHTTP Server Started\n'
fi
