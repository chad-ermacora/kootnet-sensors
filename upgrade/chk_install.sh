# HTTP Download Server Options
PIP3_INSTALL="gpiozero envirophat sense_hat bme680 bh1745 lsm303d vl53l1x smbus2 plotly matplotlib guizero request"
APT_GET_INSTALL="python3-pip fonts-freefont-ttf sense-hat lighttpd python3-smbus rpi.gpio fake-hwclock"
APT_GET_REMOVE="wolfram-engine"

# Kill any open nano & make sure folders are created
killall nano 2>/dev/null
printf '\nChecking and or Creating Required Folders\n'
mkdir /home/pi/KootNetSensors 2>/dev/null
mkdir /home/pi/KootNetSensors/backups 2>/dev/null
mkdir /home/pi/KootNetSensors/logs 2>/dev/null
mkdir /home/pi/KootNetSensors/data 2>/dev/null
mkdir /mnt/supernas 2>/dev/null
mkdir /opt/kootnet-control-center 2>/dev/null
mkdir /opt/kootnet-control-center/logs 2>/dev/null
mkdir /opt/kootnet-sensors 2>/dev/null
mkdir /opt/kootnet-sensors/auto_start 2>/dev/null
mkdir /opt/kootnet-sensors/sensor_modules 2>/dev/null
mkdir /opt/kootnet-sensors/upgrade 2>/dev/null

# Add and edit Sensors
if [ -f "/home/pi/KootNetSensors/installed_sensors.txt" ]
then
  printf '/home/pi/KootNetSensors/installed_sensors.txt OK'
else
  printf '\nSetting up Installed Sensors File\n'
  cat > /home/pi/KootNetSensors/installed_sensors.txt << "EOF"
Change the number in front of each line. Enable = 1 & Disable = 0
1 = RP_system
0 = RP_senseHAT
0 = Pimoroni_bh1745
0 = Pimoroni_BME680
0 = Pimoroni_Enviro
0 = Pimoroni_LSM303D
0 = Pimoroni_VL53L1X
EOF
  nano /home/pi/KootNetSensors/installed_sensors.txt
fi

# Add and Edit Config
if [ -f "/home/pi/KootNetSensors/config.txt" ]
then
  printf '\n/home/pi/KootNetSensors/config.txt OK\n'
else
  printf '\nSetting up Config File\n'
  cat > /home/pi/KootNetSensors/config.txt << "EOF"
Enable = 1 & Disable = 0
1 = Record Sensors to SQL Database
300 = Duration between Interval readings in Seconds
0.15 = Duration between Trigger readings in Seconds
0 = Enable Custom Settings
0.0 = Custom Accelerometer variance
0.0 = Custom Magnetometer variance
0.0 = Custom Gyroscope variance
EOF
  nano /home/pi/KootNetSensors/config.txt
fi
# Network + Other Setup
if [ -f "/home/pi/KootNetSensors/zInstalled.txt" ]
then
  printf '\nInstall Detected, Skipping Setup\n'
else
  printf '\nInstalling Config Files & Opening for edit\n'
  # Add and edit TCP/IP v4 Network + Wireless
  cp /etc/network/interfaces /home/pi/KootNetSensors/backups/ 2>/dev/null
  cat >> /etc/network/interfaces << "EOF"

# Be sure to Change the IP to match your network
#
# To let your wireless router assign the IP
# Change 'iface wlan0 inet static' to 'iface wlan0 inet dhcp'
# Then remove all lines below EXCEPT for the one with wpa-conf

allow-hotplug wlan0
iface wlan0 inet static
  address 192.168.10.254
  netmask 255.255.255.0
  gateway 192.168.10.1
  dns-nameservers 192.168.10.1
  wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf
EOF
  nano /etc/network/interfaces
  printf '\nUpdating Wireless Networks to Auto Connect to\n'
  cp /etc/wpa_supplicant/wpa_supplicant.conf /home/pi/KootNetSensors/backups/ 2>/dev/null
  cat > /etc/wpa_supplicant/wpa_supplicant.conf << "EOF"
# Be sure to update to your wireless network
#
# Which ever wireless network has more signal strength
# Is the one that will connect, assuming settings are correct
#
# To add additional wireless network connections
# Copy one of the network blocks, including both { } and
# Paste it at the bottom of the file & Modify as needed

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
  nano /etc/wpa_supplicant/wpa_supplicant.conf
  # Install needed programs and dependencies
  printf '\nStarting System Update & Upgrade, this may take awhile ...\n\n'
  # Remove wolfram-engine due to size of upgrades
  apt-get -y remove $APT_GET_REMOVE
  apt-get update
  apt-get -y upgrade
  printf '\nChecking Dependencies\n'
  apt-get -y install $APT_GET_INSTALL
  pip3 install $PIP3_INSTALL

  # Create Installed File to prevent re-runs after first run
  date > /home/pi/KootNetSensors/zInstalled.txt
fi
