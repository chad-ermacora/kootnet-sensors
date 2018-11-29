#!/usr/bin/env bash
# HTTP Download Server Options
PIP3_INSTALL="smbus2 gpiozero envirophat sense_hat bme680 bh1745 lsm303d vl53l1x guizero plotly request requests Flask gevent matplotlib"
APT_GET_INSTALL="libatlas3-base fonts-freefont-ttf sense-hat fake-hwclock"
DATA_DIR="/home/kootnet_data"
CONFIG_DIR="/etc/kootnet"

# Kill any open nano & make sure folders are created
killall nano 2>/dev/null
printf '\nChecking & creating required folders\n'
mkdir ${DATA_DIR} 2>/dev/null
mkdir ${DATA_DIR}/logs 2>/dev/null
mkdir ${DATA_DIR}/scripts 2>/dev/null
mkdir ${CONFIG_DIR} 2>/dev/null
mkdir ${CONFIG_DIR}/backups 2>/dev/null
mkdir /mnt/supernas 2>/dev/null
mkdir /opt/kootnet-control-center 2>/dev/null
mkdir /opt/kootnet-control-center/logs 2>/dev/null
mkdir /opt/kootnet-sensors 2>/dev/null
mkdir /opt/kootnet-sensors/auto_start 2>/dev/null
mkdir /opt/kootnet-sensors/sensor_modules 2>/dev/null
mkdir /opt/kootnet-sensors/scripts 2>/dev/null
# Add and edit Sensors
if [[ -f ${CONFIG_DIR}/installed_sensors.conf ]]
then
  printf ${CONFIG_DIR}"/installed_sensors.conf OK\n"
else
  printf ${CONFIG_DIR}'/installed_sensors.conf Setup\n'
  cat > ${CONFIG_DIR}/installed_sensors.conf << "EOF"
Change the number in front of each line. Enable = 1 & Disable = 0
1 = Gnu/Linux System (Raspbian, Debian, etc)
0 = Raspberry Pi Zero W
0 = Raspberry Pi 3BPlus
0 = Raspberry Pi Sense HAT
0 = Pimoroni BH1745
0 = Pimoroni BME680
0 = Pimoroni EnviroPHAT
0 = Pimoroni LSM303D
0 = Pimoroni VL53L1X
EOF
  nano ${CONFIG_DIR}/installed_sensors.conf
fi
# Add and Edit Config
if [[ -f ${CONFIG_DIR}"/sql_recording.conf" ]]
then
  printf ${CONFIG_DIR}"/sql_recording.conf OK\n"
else
  printf ${CONFIG_DIR}"/sql_recording.conf Setup\n"
  cat > ${CONFIG_DIR}/sql_recording.conf << "EOF"
Enable = 1 & Disable = 0 (Recommended: Don't change anything)
1 = Record Sensors to SQL Database
300 = Duration between Interval readings in Seconds
0.15 = Duration between Trigger readings in Seconds
0 = Enable Custom Settings
0.0 = Custom Accelerometer variance
0.0 = Custom Magnetometer variance
0.0 = Custom Gyroscope variance
0 = Enable Custom Temperature Offset
0.0 = Current Temperature Offset
EOF
  nano ${CONFIG_DIR}/sql_recording.conf
fi
# Network + Other Setup
if [[ -f ${CONFIG_DIR}"/installed_datetime.txt" ]]
then
  printf '\nPrevious install detected, skipping setup\n'
else
  printf '\nInstalling config files\n'
  # Add and edit TCP/IP v4 Network + Wireless
  cp -f /etc/network/interfaces ${CONFIG_DIR}/backups/ 2>/dev/null
  cat >> /etc/network/interfaces << "EOF"

allow-hotplug wlan0
iface wlan0 inet static
  # Be sure to Change the IP settings to match your network
  address 192.168.10.254
  netmask 255.255.255.0
  gateway 192.168.10.1
  dns-nameservers 192.168.10.1
  wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf
EOF
  nano /etc/network/interfaces
  printf '\nUpdating automatic wireless network connections\n'
  cp -f /etc/wpa_supplicant/wpa_supplicant.conf ${CONFIG_DIR}/backups/ 2>/dev/null
  cat > /etc/wpa_supplicant/wpa_supplicant.conf << "EOF"
# Update or Add additional wireless network connections as required
# Add your wireless name to the end of 'ssid=' & password to the end of 'psk=' in double quotes

ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

# Change 'country' to your country, common codes are included below
# GB (United Kingdom), FR (France), US (United States), CA (Canada)
country=CA

network={
        ssid="SensorWifi"
        psk="2505512335"
        key_mgmt=WPA-PSK
}
network={
        ssid="SomeOtherNetwork"
        psk="SuperSecurePassword"
        key_mgmt=WPA-PSK
}
EOF
  nano /etc/wpa_supplicant/wpa_supplicant.conf
  # Install needed programs and dependencies
  printf '\nStarting system update & upgrade. This may take awhile ...\n\n'
  apt-get update
  apt-get -y upgrade
  printf '\nChecking dependencies\n'
  apt-get -y install ${APT_GET_INSTALL}
  python3 -m pip install -U pip
  pip3 install ${PIP3_INSTALL}
  # Create Installed File to prevent re-runs.  Create install_version file for program first run.
  date > ${CONFIG_DIR}/installed_datetime.txt
  date > ${CONFIG_DIR}/installed_version.txt
fi
