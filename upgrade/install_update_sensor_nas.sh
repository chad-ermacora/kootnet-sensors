# This will copy all the needed files, install the dependencies and update the system
# In crontab under root, scripts are auto run to keep 3 programs running as well as
# The primary interval sensor program recording to a SQL DB. 
# Later to do -> apparently anything added to cli during run, such as ./script.sh me me2
# Is accessable in the script through $1 $2 etc. 
clear
if [ -f "/home/pi/config/sensor_type.txt" ]
then
  printf '\n'
else
  printf 'Starting Install\n\n'
  mkdir /home/pi/config 2>/dev/null
  cat > /home/pi/config/sensor_type.txt << "EOF"
Change the number in front of each line. Enable = 1 & Disable = 0
1 = RP_system
0 = RP_senseHAT
0 = Pimoroni_bh1745
0 = Pimoroni_BME680
1 = Pimoroni_Enviro
0 = Pimoroni_LSM303D
0 = Pimoroni_VL53L1X
EOF
  nano /home/pi/config/sensor_type.txt
fi
printf 'Checking & Making Folders\n\n'
mkdir /mnt/supernas 2>/dev/null
mkdir /home/sensors 2>/dev/null
mkdir /home/sensors/auto_start 2>/dev/null
mkdir /home/sensors/sensor_modules 2>/dev/null
mkdir /home/sensors/upgrade 2>/dev/null
mkdir /home/sensors/data 2>/dev/null
mkdir /home/sensors/data/Old 2>/dev/null
printf 'Connecting to NAS and Copying Files\n\n'
mount -t cifs //192.168.7.15/Public /mnt/supernas -o username=myself,password='123'
sleep 1
cp -R /mnt/supernas/RaspberryPi/Sensors/ClientSensors/* /home/sensors
cp /home/sensors/upgrade/install_update_sensor_nas.sh /home/pi/update_sensor_nas.sh
cp /home/sensors/test* /home/pi 
printf 'Configuring root crontab with\n'
printf '1. sensorIntervalToDataBase.py (Run every 5 min to record to DB)\n'
printf '2. autoStartTriggerToDataBase.sh (Run every 1 min to start if NOT running)\n'
printf '3. autoStartCommands.sh (Run every 1 min to start if NOT running)\n'
printf '4. autoStartHTTP.sh (Run every 1 min to start if NOT running)\n'
printf '5. fake-hwclock (Run every 1 min to save current time to file loads file on boot)\n'
echo '*/5 * * * * python3 /home/sensors/sensorIntervalToDataBase.py' > /home/pi/tmp34441.txt
echo '*/1 * * * * bash /home/sensors/auto_start/autoStartCommands.sh' >> /home/pi/tmp34441.txt
echo '*/1 * * * * bash /home/sensors/auto_start/autoStartHTTP.sh' >> /home/pi/tmp34441.txt
echo '*/1 * * * * bash /home/sensors/auto_start/autoStartTriggerToDataBase.sh' >> /home/pi/tmp34441.txt
echo '*/1 * * * * fake-hwclock' >> /home/pi/tmp34441.txt
crontab -u root /home/pi/tmp34441.txt
printf 'Updating wpa_supplicant.conf\n'
cat > /etc/wpa_supplicant/wpa_supplicant.conf << "EOF"
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=CA

network={
        ssid="SensorWifi"
        psk="2505512335"
        key_mgmt=WPA-PSK
}
network={
        ssid="KI-WiFi"
        psk="2505510208"
        key_mgmt=WPA-PSK
}
EOF
umount /mnt/supernas
rm /home/pi/tmp34441.txt
printf '\n\nSetting Permissions\n' 
chmod 754 /home/pi/*.sh
chmod 754 /home/pi/*.py
chmod 644 /home/pi/config/*
chmod 755 /home/sensors -R
chmod 754 /home/sensors/*.py
chmod 754 /home/sensors/auto_start/*.sh
chmod 754 /home/sensors/upgrade/*.sh
chmod 664 /home/sensors/data/*.sqlite 2>/dev/null
chmod 664 /home/sensors/data/Old/* 2>/dev/null
chown pi:root /home/pi -R
chown pi:root /home/sensors -R
chown pi:root /home/pi/update_sensor_nas.sh
chown pi:root /home/pi/test*
chmod 777 /var/log/lighttpd -R 2>/dev/null
if [ -f "/home/pi/config/zInstalled" ]
then
  printf 'Update Done\n'
else
  printf '\nStarting System Update, this will take awhile...\n'
  apt-get -y remove wolfram-engine
  apt-get update
  apt-get -y upgrade
  printf '\nInstalling Dependencies\n\n'
  apt-get -y install python3-pip fonts-freefont-ttf sense-hat lighttpd python3-smbus rpi.gpio fake-hwclock
  pip3 install gpiozero envirophat sense_hat bme680 bh1745 lsm303d vl53l1x smbus2 
  printf '\nConfiguring Network\n'
  cat >> /etc/network/interfaces << "EOF"

allow-hotplug wlan0
iface wlan0 inet static
  address 192.168.10.254
  netmask 255.255.255.0
  gateway 192.168.10.1
  dns-nameservers 192.168.10.1
  wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf
EOF
  date > /home/pi/config/zInstalled
  printf '\nInstall Done\n\n'
  nano /etc/network/interfaces
fi
date > /home/pi/config/LastUpdated.txt
echo ' Updated with SMB/NAS ' >> /home/pi/config/LastUpdated.txt
