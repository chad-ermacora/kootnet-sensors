#!/usr/bin/env bash
# HTTP Download Server Options
APT_GET_INSTALL="python3-pip python3-venv libatlas3-base fonts-freefont-ttf sense-hat fake-hwclock cifs-utils"
DATA_DIR="/home/kootnet_data"  # This is hardcoded into linux services
CONFIG_DIR="/etc/kootnet"
# Add and edit Sensors
if [[ -f ${CONFIG_DIR}/installed_sensors.conf ]]
then
  printf ${CONFIG_DIR}"/installed_sensors.conf OK\n"
else
  printf ${CONFIG_DIR}'/installed_sensors.conf Setup\n'
  cat > ${CONFIG_DIR}/installed_sensors.conf << "EOF"
Change the number in front of each line. Enable = 1 & Disable = 0
1 = Gnu/Linux - Raspbian
0 = Raspberry Pi Zero W
0 = Raspberry Pi 3BPlus
0 = Raspberry Pi Sense HAT
0 = Pimoroni BH1745
0 = Pimoroni AS7262
0 = Pimoroni BMP280
0 = Pimoroni BME680
0 = Pimoroni EnviroPHAT
0 = Pimoroni Enviro+ (Plus)
0 = Pimoroni LSM303D
0 = Pimoroni ICM20948
0 = Pimoroni VL53L1X
0 = Pimoroni LTR-559
0 = Pimoroni VEML6075
EOF
  nano ${CONFIG_DIR}/installed_sensors.conf
fi
# Add and Edit Config
if [[ -f ${CONFIG_DIR}"/sql_recording.conf" ]]
then
  printf ${CONFIG_DIR}"/sql_recording.conf OK\n"
else
  printf ${CONFIG_DIR}"/sql_recording.conf Setup\n"
  # Used "Custom" in config here for install, but program will replace with "Current"
  cat > ${CONFIG_DIR}/sql_recording.conf << "EOF"
Enable = 1 & Disable = 0 (Recommended: Do not change if you are unsure)
0 = Enable Debug Logging
1 = Record Interval Sensors to SQL Database
0 = Record Trigger Sensors to SQL Database
300.0 = Seconds between Interval recordings
0 = Enable Custom Temperature Offset
0.0 = Custom Temperature Offset
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
# Add your wireless name to the end of 'ssid='
# Add the password to the end of 'psk=' in double quotes

ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

# Change 'country' to your country, common codes are included below
# GB (United Kingdom), FR (France), US (United States), CA (Canada)
country=CA

network={
        ssid="SensorWifi"
        scan_ssid=1
        psk="2505512335"
        key_mgmt=WPA-PSK
}
network={
        ssid="SomeOtherNetwork"
        scan_ssid=1
        psk="SuperSecurePassword"
        key_mgmt=WPA-PSK
}
EOF
  nano /etc/wpa_supplicant/wpa_supplicant.conf
  # Install needed programs and dependencies
  printf '\nStarting system update. This may take awhile ...\n\n'
  apt-get update
#  apt-get -y upgrade
  printf '\nChecking dependencies\n'
  apt-get -y install ${APT_GET_INSTALL}
  cd ${DATA_DIR}
  python3 -m venv --system-site-packages python-env
  source ${DATA_DIR}/python-env/bin/activate
  python3 -m pip install -U pip
  pip3 install -r /opt/kootnet-sensors/requirements.txt
  cat > ${CONFIG_DIR}/installed_version.txt << "EOF"
New_Install.99.999
EOF
  deactivate
  # Create Installed File to prevent re-runs.  Create install_version file for program first run.
  date > ${CONFIG_DIR}/installed_datetime.txt
fi
