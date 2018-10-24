clear
printf '\n\nDoing "Clean" Upgrade\nLeaves Database and Config\nDeletes everything else\nRe-Downloads and Installs\n'
cp /opt/kootnet-sensors/upgrade/update_programs_online.sh /root
rm /home/pi/*.sh* 2>/dev/null
rm /home/pi/*.py* 2>/dev/null
rm -R -f /opt/kootnet-sensors 2>/dev/null
rm -R -f /opt/kootnet-control-center 2>/dev/null
rm -f /home/pi/Desktop/KootNet-Control-Center.desktop 2>/dev/null
bash /root/update_programs_online.sh
