#!/usr/bin/env bash
# HTTP Download Server Options
APT_GET_INSTALL="python3-pip python3-venv libatlas3-base fonts-freefont-ttf sense-hat fake-hwclock cifs-utils libfreetype6-dev libjpeg-dev build-essential"
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
0 = Pimoroni 11x7 LED Matrix
0 = Pimoroni 10.96'' SPI Colour LCD (160x80)
0 = Pimoroni 1.12'' Mono OLED (128x128, white/black)
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
1 = Enable Display (If present)
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

0 = Enable CPU Temperature
5.0 = CPU Temperature variance
1.0 = Seconds between 'CPU Temperature' readings

0 = Enable Environmental Temperature
5.0 = Environmental Temperature variance
1.0 = Seconds between 'Environmental Temperature' readings

0 = Enable Pressure
10 = Pressure variance
1.0 = Seconds between 'Pressure' readings

0 = Enable Altitude
10 = Altitude variance
1.0 = Seconds between 'Altitude' readings

0 = Enable Humidity
5.0 = Humidity variance
1.0 = Seconds between 'Humidity' readings

0 = Enable Distance
5.0 = Distance variance
1.0 = Seconds between 'Distance' readings

0 = Enable Gas
100.0 = Gas Resistance Index variance
100.0 = Gas Oxidising variance
100.0 = Gas Reducing variance
100.0 = Gas NH3 variance
30.0 = Seconds between 'Gas' readings

0 = Enable Particulate Matter (PM)
4.0 = Particulate Matter 1 (PM1) variance
4.0 = Particulate Matter 2.5 (PM2.5) variance
4.0 = Particulate Matter 10 (PM10) variance
60.0 = Seconds between 'Particulate Matter' readings

0 = Enable Lumen
100.0 = Lumen variance
1.0 = Seconds between 'Lumen' readings

0 = Enable Colour
15.0 = Red variance
15.0 = Orange variance
15.0 = Yellow variance
15.0 = Green variance
15.0 = Blue variance
15.0 = Violet variance
10.0 = Seconds between 'Colour' readings

0 = Enable Ultra Violet
5.0 = Ultra Violet Index variance
10.0 = Ultra Violet A variance
10.0 = Ultra Violet B variance
5.0 = Seconds between 'Ultra Violet' readings

0 = Enable Accelerometer
0.1 = Accelerometer X variance
0.1 = Accelerometer Y variance
0.1 = Accelerometer Z variance
0.25 = Seconds between 'Accelerometer' readings

0 = Enable Magnetometer
25.0 = Magnetometer X variance
25.0 = Magnetometer Y variance
25.0 = Magnetometer Z variance
0.25 = Seconds between 'Magnetometer' readings

0 = Enable Gyroscope
25.0 = Gyroscope X variance
25.0 = Gyroscope Y variance
25.0 = Gyroscope Z variance
0.25 = Seconds between 'Gyroscope' readings
EOF
  nano ${CONFIG_DIR}/trigger_variances.conf
fi
# Network + Other Setup
if [[ -f ${CONFIG_DIR}"/installed_datetime.txt" ]]
then
  printf '\nPrevious install detected, skipping setup\n'
else
  # Install needed programs and dependencies
  printf '\nStarting Dependency Install. This may take awhile ...\n\n'
  apt-get update
  apt-get -y install ${APT_GET_INSTALL}
  cd ${DATA_DIR} || exit
  python3 -m venv --system-site-packages python-env
  source ${DATA_DIR}/python-env/bin/activate
  python3 -m pip install -U pip
  pip3 install -r /opt/kootnet-sensors/requirements.txt
  # Set HTTP Authentication
  clear
  printf 'Dependencies Installed\n\n'
  bash /opt/kootnet-sensors/scripts/change_http_authentication.sh
  cat > ${CONFIG_DIR}/installed_version.txt << "EOF"
New_Install.99.999
EOF
  deactivate
  # Create Installed File to prevent re-runs.  Create install_version file for program first run.
  date > ${CONFIG_DIR}/installed_datetime.txt
fi
