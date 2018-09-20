# This will copy all the needed files, install the dependencies and update the system
# In crontab under root, scripts are auto run to keep 3 programs running as well as
# The primary interval sensor program recording to a SQL DB. 
if [ -f "/home/pi/config/zInstalled.txt" ]
then
  printf '\n\nSensors Already Installed, Opening Configuration Files Only\n\n'
  nano /home/pi/config/sensor_type.txt
else
  printf '\n\nStarting KootNet Sensor Install\n\n'
  mkdir /home/pi/config 2>/dev/null
  cat > /home/pi/config/sensor_type.txt << "EOF"
Change the number in front of each line. Enable = 1 & Disable = 0
1 = RP_system
0 = RP_senseHAT
0 = Pimoroni_bh1745
0 = Pimoroni_BME680
0 = Pimoroni_Enviro
0 = Pimoroni_LSM303D
0 = Pimoroni_VL53L1X
EOF
  nano /home/pi/config/sensor_type.txt
  # Make sure folders are created
  printf 'Checking & Making Folders\n\n'
  mkdir /mnt/supernas 2>/dev/null
  mkdir /home/sensors 2>/dev/null
  mkdir /home/sensors/auto_start 2>/dev/null
  mkdir /home/sensors/sensor_modules 2>/dev/null
  mkdir /home/sensors/upgrade 2>/dev/null
  mkdir /home/sensors/data 2>/dev/null
  mkdir /home/sensors/data/Old 2>/dev/null
  # Create folder in root, download files, then install
  printf '\nCopying Program to system ... \n'
  mkdir /root/SensorInstallFiles 2>/dev/null
  cd /root/SensorInstallFiles
  wget -r -np -nH -R "index.html*" http://kootenay-networks.com/utils/koot_net_sensors/Installers/raw_files/sensor-rp/
  cp -R /root/SensorInstallFiles/utils/koot_net_sensors/Installers/raw_files/sensor-rp/* /home/sensors/
  # Add easy upgrade, config edits & sensor test app(s) to user pi's home directory
  cp /home/sensors/upgrade/update_programs_online.sh /home/pi/update_sensor_online.sh
  cp /home/sensors/upgrade/install_sensors.sh /home/pi/sensor_edit_configs.sh
  cp /home/sensors/test* /home/pi 2>/dev/null
  # Upgrade System and install sensor Dependencies
  printf '\nStarting System Update, this will take awhile...\n'
  # Remove wolfram-egine due to size of upgrades
  apt-get -y remove wolfram-engine
  apt-get update
  apt-get -y upgrade
  printf '\nInstalling Dependencies\n\n'
  apt-get -y install python3-pip fonts-freefont-ttf sense-hat lighttpd python3-smbus rpi.gpio fake-hwclock
  pip3 install gpiozero envirophat sense_hat bme680 bh1745 lsm303d vl53l1x smbus2
  # Add and edit TCP/IP v4 Network + Wireless
  printf '\nConfiguring Network\n'
  cat >> /etc/network/interfaces << "EOF"

# Be sure to Change the IP to match your network
allow-hotplug wlan0
iface wlan0 inet static
  address 192.168.10.254
  netmask 255.255.255.0
  gateway 192.168.10.1
  dns-nameservers 192.168.10.1
  wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf
EOF
  cat > /etc/wpa_supplicant/wpa_supplicant.conf << "EOF"
# Be sure to update to your networks Needs.
# Add additional network sections to auto connect to other networks when in range. 
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
  date > /home/pi/config/zInstalled.txt
  # Install crontab entries
  bash /home/sensors/upgrade/update_crontab.sh
  # Make sure permissions are correct
  bash /home/sensors/upgrade/update_file_permissions.sh
  printf '\nInstall Done\n\n'
fi
nano /etc/network/interfaces
nano /etc/wpa_supplicant/wpa_supplicant.conf
killall python3
printf '\nPlease wait up to 60 Seconds for Sensor to come online\n\n'
