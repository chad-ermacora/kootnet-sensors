# Kootnet Sensors - RPi Sensor Recording Software
This program is used to record sensor readings on a Raspberry Pi to an SQLite3 database or transfer sensor data to 
another sensor or service using MQTT. Add one or more of the 21+ supported sensors.  

Sensor types include heat, pressure, altitude, humidity, distance, gas, particulate matter 1/2.5/4/10, light, 
color, ultra-violet, acceleration, electromagnetic fields, angular velocity (gyroscope) & GPS coordinates.

Features include a Web Portal to graph, view live readings, generate reports, 
upload data to 3rd party weather services and more!  

[Project Website](https://kootenay-networks.com/?page_id=170)  

Installing, Updating & Removing
-------------------------
**Supported Operating Systems**: Raspberry Pi OS & Ubuntu  
**Note**: *Kootnet Sensors should work on Debian and other Debian based systems that support Python 3.5 or higher.* 

**Supported Hardware for Sensor Recording**  
**Note**: *Other branded sensors with the same chip should work. 
Enabling the Pimoroni BME680 should work for the Adafruit BME680 for example.*  

**[Raspberry Pi](https://www.raspberrypi.org/products/)**  
**System Boards**: Zero W, 3x, 4x and probably other RPi's, but they are untested  
**Combo Sensors**: Sense HAT

**[Pimoroni](https://shop.pimoroni.com/)**  
**Displays**: 11x7 LED Matrix, 1.12" Mono OLED (128x128, white/black), 0.96" SPI Colour LCD (160x80)  
**Temperature**: *MCP9600  
**Color/Light**: AS7262, BH1745, VEML6075  
**Combo Sensors**: Enviro, Enviro+, EnviroPHAT, BME680, BME280, BMP280, LTR-559  
**Volatile Organic Compounds**: SGP30  
**Particulate Matter**: PMS5003  
**Distance**: VL53L1X  
**Accelerometer/Magnetometer/Gyroscope**: ICM20948, LSM303D, MSA301  
**Global Positioning System**: PA1010D  
**Real Time Clock**: RV3028

**Maxim/Dallas**  
**Temperature**: *DS1822, *DS18S20, *DS18B20, *DS1825, *DS28EA00, *MAX31850K  

**Sensirion**  
**Particulate Matter**: SPS30  

**Note**: *Sensors names starting with a * are untested sensors.*

If you have a Debian desktop environment, you can simply 
[download this file](https://kootenay-networks.com/installers/KootnetSensors.deb) and double click to install.  
After the installation is done, open https://localhost:10065 on the Raspberry Pi itself to configure and use the sensor.  
If you are installing from the command line, run the following command in a terminal.  

```
wget -O KootnetSensors.deb https://kootenay-networks.com/installers/KootnetSensors.deb && sudo apt-get update && sudo apt-get -y install ./KootnetSensors.deb
```

To uninstall Kootnet Sensors, run the following command in a terminal.  
**Note**: *You can also find kootnet-sensors in your Operating System's package manager.*
```
sudo apt-get remove kootnet-sensors
```

Manually Download & Run
-------------------------

Although not recommended, you can download the source code directly and run it from a terminal.  
Follow the instructions below to install prerequisites. 

**Note**: *Kootnet Sensors will not autostart when using this method*  
**Note**: *Program updates will be disabled*  
**Note**: *You only need to run steps 2-4 once, to start Kootnet Sensors after that, follow steps 1 & 5 only*

1. Open a terminal window
2. Download and extract Kootnet Sensors
```
wget https://github.com/chad-ermacora/kootnet-sensors/archive/refs/tags/Beta.34.145.tar.gz

mkdir ~/kootnet_sensors && tar -xvzf Beta.34.145.tar.gz --directory ~/kootnet_sensors --strip-components=1
```

3. Install prerequisites by running the following commands one after another (each line is a command). 
```
sudo apt-get update && sudo apt-get -y install python3 python3-venv python3-pip python3-dev bash wget openssl libssl-dev

python3 -m venv ~/ks_venv

~/ks_venv/bin/python3 -m pip install -U pip

~/ks_venv/bin/pip3 install -r ~/kootnet_sensors/requirements.txt
```

4. If you are using a Raspberry Pi run these, if not, skip to step 5
```
sudo apt-get -y install libffi-dev libatlas3-base fake-hwclock libopenjp2-7 libtiff-dev

~/ks_venv/bin/pip3 install -r ~/kootnet_sensors/requirements_hw_sensors.txt
```

5. Start Kootnet Sensors 

```
sudo ~/ks_venv/bin/python3 ~/kootnet_sensors/start_sensor_services.py
```

Controlling the Sensor
-------------------------

**Kootnet Sensors** has a built-in HTTPS server (Web Portal) to monitor, manage and operate the Sensor.  
There is also a 'Remote Management' section in the Web Portal for managing one or more remote sensors.  
Assuming the sensor's IP is 192.168.10.11, you can access the sensor at https://192.168.10.11:10065 
from any device with a web browser on the same network. 

**Default Web Portal Login**  
*User*: Kootnet  
*Password*: sensors

**Recommended**: *Change the default Web Portal username and password after install.*  
**Note**: *Find shortcuts to edit configurations and access the Web Portal in the operating systems main menu.*  

Configurations can also be changed using the terminal by running the following command.
```
sudo /home/kootnet_data/env/bin/python /opt/kootnet-sensors/start_cli_edit_config.py
```

Sensor System Service
----------

'KootnetSensors' is the GNU/Linux systemd service that automatically starts Kootnet Sensors. 

**The following terminal command disables and stops KootnetSensors**
```
sudo systemctl disable KootnetSensors && sudo systemctl stop KootnetSensors
```
**The following terminal command enables and starts KootnetSensors**
```
sudo systemctl enable KootnetSensors && sudo systemctl start KootnetSensors
```
Example Raspberry Pi Sensor Units
---------------------
![KootNet Sensors - Raspberry Pi Sensors](http_server/extras/SensorHardware.jpg "Raspberry Pi Sensors")
