clear
printf '\n\nDoing "Clean" Upgrade\nLeaves Database and Config\nDeletes everything else\nRe-Downloads and Installs\n'
cp /home/sensors/upgrade/update_programs_online.sh /root
rm /home/pi/*.sh 2>/dev/null
rm /home/pi/*.py 2>/dev/null
rm -R /home/sensors 2>/dev/null
bash /root/update_programs_online.sh
