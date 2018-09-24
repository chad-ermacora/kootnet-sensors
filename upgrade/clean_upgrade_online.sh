clear
printf '\n\nDoing "Clean" Upgrade\nLeaves Database and Config\nDeletes everything else\nRe-Downloads and Installs\n'
rm /home/pi/*.sh 2>/dev/null
rm /home/pi/*.py 2>/dev/null
rm -R /home/sensors 2>/dev/null
# Remove old installer files and download new
rm -R /root/CleanInstallFiles 2>/dev/null
mkdir /root/CleanInstallFiles 2>/dev/null
mkdir /home/sensors 2>/dev/null
cd /root/CleanInstallFiles
# Download program files off KootNet HTTP Server
wget -r -np -nH -R "index.html*" http://kootenay-networks.com/utils/koot_net_sensors/Installers/raw_files/sensor-rp/
clear
printf '\nFiles Downloaded from KootNet HTTP Server\n\nStarting Install\n'
cp -R /root/CleanInstallFiles/utils/koot_net_sensors/Installers/raw_files/sensor-rp/* /home/sensors/
bash /home/sensors/upgrade/update_programs_online.sh
killall python3
ls -l /home/sensors
printf '\n\nDone\n' 
