# Kootnet Sensors - RPi Sensor Recording Software
This program is used to record sensor readings on a Raspberry Pi to an SQLite3 database.  
Add one or more of the 14+ supported sensors to record and view readings of your choice.  

Sensor types include heat, pressure, altitude, humidity, distance, gas, particulate matter 1/2.5/10, light, 
color, ultra violet, acceleration, electromagnetic fields and angular velocity (gyroscope).

Features include a Web Portal to graph, view live readings, generate reports, upload data to 3rd party weather services and more!  

[Project Website](http://kootenay-networks.com/?page_id=170)  
[KootNet Sensors - Control Center](https://github.com/chad-ermacora/sensor-control-center) - Companion App (Depreciated)

Installing, Updating & Removing
-------------------------
**Supported Systems**: Raspbian & other Debian based Operating Systems  
*Note: Only tested on Raspbian and Ubuntu* 

If you have a Debian desktop environment, you can simply 
[download this file](http://kootenay-networks.com/installers/KootnetSensors.deb) and double click to install.  
After the install is done, open https://localhost:10065 on the Raspberry Pi itself to configure the sensor.  
If you are installing from the command line, run the following command in a terminal.  

```
wget -O KootnetSensors.deb http://kootenay-networks.com/installers/KootnetSensors.deb && sudo apt-get update && sudo apt-get -y install ./KootnetSensors.deb
```

To uninstall Kootnet Sensors, run the following command in a terminal OR find kootnet-sensors in your systems software manager.  
(Since Version Alpha.28.140)
```
sudo apt-get remove kootnet-sensors
```

Controlling the Sensor
-------------------------

**Kootnet Sensors** has a built in HTTPS server (Web Portal) to help monitor and manage the individual sensor.  
There is also a 'Sensor Control' section in the Web Portal for managing one or more remote sensors.  
Assuming the sensor's IP is 192.168.10.11, you can access the sensor at https://192.168.10.11:10065

**Default Web Portal Login**  
*User*: Kootnet  
*Pass*: sensors

Configurations can also be changed through the terminal by running the following command.  
**Note**: *Web Portal Login credentials can ONLY be changed through the terminal command below.*  
**Note**: *Find shortcuts to both the Web Portal and terminal script to edit configurations in the operating systems menu.*  
**Note**: *It is recommended to run the terminal command after install to change the default Web Portal username and password*

```
sudo bash /opt/kootnet-sensors/edit_sensor_config.sh
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
![KootNet Sensors - Raspberry Pi Sensors](extras/SensorHardware.jpg "Raspberry Pi Sensors")
