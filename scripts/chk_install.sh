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
0 = Pimoroni Enviro+
0 = Pimoroni PMS5003
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
# Add and Edit Variance Trigger Recording settings
if [[ -f ${CONFIG_DIR}"/trigger_variances.conf" ]]
then
  printf ${CONFIG_DIR}"/trigger_variances.conf OK\n"
else
  printf ${CONFIG_DIR}"/trigger_variances.conf Setup\n"
  cat > ${CONFIG_DIR}/trigger_variances.conf << "EOF"
Enable or Disable & set Variance settings.  0 = Disabled, 1 = Enabled.
1 = Enable Sensor Uptime
1209600.0 = Seconds between SQL Writes of Sensor Uptime

1 = Enable CPU Temperature
10.0 = CPU Temperature variance
600.0 = Seconds between 'CPU Temperature' readings

1 = Enable Environmental Temperature
10.0 = Environmental Temperature variance
600.0 = Seconds between 'Environmental Temperature' readings

1 = Enable Pressure
50 = Pressure variance
300.0 = Seconds between 'Pressure' readings

1 = Enable Altitude
50 = Altitude variance
300.0 = Seconds between 'Altitude' readings

1 = Enable Humidity
10.0 = Humidity variance
600.0 = Seconds between 'Humidity' readings

1 = Enable Distance
10.0 = Distance variance
600.0 = Seconds between 'Distance' readings

1 = Enable Gas Resistance Index
10.0 = Gas Resistance Index variance
600.0 = Seconds between 'Gas Resistance Index' readings

1 = Enable Gas Oxidising
10.0 = Gas Oxidising variance
600.0 = Seconds between 'Gas Oxidising' readings

1 = Enable Gas Reducing
10.0 = Gas Reducing variance
600.0 = Seconds between 'Gas Reducing' readings

1 = Enable Gas NH3
10.0 = Gas NH3 variance
600.0 = Seconds between 'Gas NH3' readings

1 = Enable Particulate Matter 1 (PM1)
10.0 = Particulate Matter 1 (PM1) variance
600.0 = Seconds between 'Particulate Matter 1 (PM1)' readings

1 = Enable Particulate Matter 2.5 (PM2.5)
10.0 = Particulate Matter 2.5 (PM2.5) variance
600.0 = Seconds between 'Particulate Matter 2.5 (PM2.5)' readings

1 = Enable Particulate Matter 10 (PM10)
10.0 = Particulate Matter 10 (PM10) variance
600.0 = Seconds between 'Particulate Matter 10 (PM10)' readings

1 = Enable Lumen
200.0 = Lumen variance
600.0 = Seconds between 'Lumen' readings

1 = Enable Red
25.0 = Red variance
300.0 = Seconds between 'Red' readings

1 = Enable Orange
25.0 = Orange variance
300.0 = Seconds between 'Orange' readings

1 = Enable Yellow
25.0 = Yellow variance
300.0 = Seconds between 'Yellow' readings

1 = Enable Green
25.0 = Green variance
300.0 = Seconds between 'Green' readings

1 = Enable Blue
25.0 = Blue variance
300.0 = Seconds between 'Blue' readings

1 = Enable Violet
25.0 = Violet variance
300.0 = Seconds between 'Violet' readings

1 = Enable Ultra Violet Index
25.0 = Ultra Violet Index variance
300.0 = Seconds between 'Ultra Violet Index' readings

1 = Enable Ultra Violet A
25.0 = Ultra Violet A variance
300.0 = Seconds between 'Ultra Violet A' readings

1 = Enable Ultra Violet B
25.0 = Ultra Violet B variance
300.0 = Seconds between 'Ultra Violet B' readings

1 = Enable Accelerometer
99999.99 = Accelerometer variance
0.15 = Seconds between 'Accelerometer' readings

1 = Enable Magnetometer
99999.99 = Magnetometer variance
0.15 = Seconds between 'Magnetometer' readings

1 = Enable Gyroscope
99999.99 = Gyroscope variance
0.15 = Seconds between 'Gyroscope' readings
EOF
  nano ${CONFIG_DIR}/trigger_variances.conf
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
