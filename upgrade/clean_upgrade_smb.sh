clear
printf '\n\nDoing "Clean" Upgrade\nLeaves Database and Config\nDeletes everything else\nRe-Downloads and Installs\n'
cp /home/sensors/upgrade/update_programs_smb.sh /home/pi/temp_upgrade_smb.sh
rm /home/pi/*.sh* 2>/dev/null
rm /home/pi/*.py* 2>/dev/null
rm -R -f /home/sensors 2>/dev/null
bash /home/pi/temp_upgrade_smb.sh
rm -f /home/pi/temp_upgrade_smb.sh
