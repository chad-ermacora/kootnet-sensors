clear
printf '\n\nDoing "Clean" upgrade\nLeaves database & config\nDeletes everything else\nThen re-downloads and installs\n'
cp /opt/kootnet-sensors/upgrade/update_programs_smb.sh /root
rm /home/pi/*.sh* 2>/dev/null
rm /home/pi/*.py* 2>/dev/null
rm -R -f /home/sensors 2>/dev/null
rm -R -f /opt/kootnet-sensors 2>/dev/null
rm -R -f /opt/kootnet-control-center 2>/dev/null
rm -f /home/pi/Desktop/KootNet-Control-Center.desktop 2>/dev/null
bash /root/update_programs_smb.sh
