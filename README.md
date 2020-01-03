# Kootnet Sensors - Raspberry Pi Sensor Software
This Program is used to record sensor readings to a SQLite3 database and manage one or more Sensors through the included management web pages.  
This can also be installed on Ubuntu in order to use the 'Sensor Control' management page.

[Project Website](http://kootenay-networks.com/?page_id=170)  
[KootNet Sensors Downloads and Instructions](http://kootenay-networks.com/?page_id=236)  
[KootNet Sensors - Control Center](https://github.com/chad-ermacora/sensor-control-center)

Installing on a Raspberry Pi (Any Model)
-------------------------

The short version of installing on a Pi is to install Raspbian and run the following 2 commands in a terminal, one after another. 
After the install is done, open the following URL on the Pi itself to configure the sensor.
https://localhost:10065/

```
wget -O KootnetSensors.deb http://kootenay-networks.com/installers/KootnetSensors.deb && sudo apt-get update && sudo apt-get -y install ./KootnetSensors.deb
```

To uninstall Kootnet Sensors, run the following command in a terminal.  
(Since Version Alpha.28.140)
```
sudo apt-get remove kootnet-sensors
```

Controlling the Sensor
-------------------------

**Kootnet Sensors** has a built in HTTPS server to help monitor and manage the individual sensor.  
There is also a 'Sensor Control' section for managing one or more remote sensors at a time.  
Assuming the sensor's IP is 192.168.10.11, you can access the sensor at https://192.168.10.11:10065

Sensor System Service
----------

The following is a Linux systemd services that automatically starts with the system and restarts if terminated. 

**KootnetSensors**
>Starts the HTTPS management portal & SQLite3 Sensor Recording program.

**The following Terminal command disables and stops KootnetSensors.**
```
sudo systemctl disable KootnetSensors && sudo systemctl stop KootnetSensors
```
**The following Terminal command enables and starts KootnetSensors.**
```
sudo systemctl enable KootnetSensors && sudo systemctl start KootnetSensors
```
Example Raspberry Pi Sensor Units
---------------------
![KootNet Sensors - Raspberry Pi Sensors](extras/SensorHardware.jpg "Raspberry Pi Sensors")
