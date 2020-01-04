# Kootnet Sensors - Raspberry Pi Sensor Software
This Program is used to record sensor readings to a SQLite3 database.  
Add one or more of the 14+ supported sensors then monitor and manage through the built in Web Portal.  
Features include graphing, live readings, report generation, Online 3rd party weather services and more!  
This can also be installed on other Debian based systems like Ubuntu for the ability to manage one or more remote sensor(s).

[Project Website](http://kootenay-networks.com/?page_id=170)  
[KootNet Sensors Downloads and Instructions](http://kootenay-networks.com/?page_id=236)  
[KootNet Sensors - Control Center](https://github.com/chad-ermacora/sensor-control-center)

Installing on a Raspberry Pi (Any Model)
-------------------------

If you have a Debian desktop environment, you can simply 
[download this file](http://kootenay-networks.com/installers/KootnetSensors.deb) and double click to install.  
After the install is done, open https://localhost:10065 on the Pi itself to configure the sensor  
If you are installing from the command line, run the following command in a terminal.  

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

**Default Web Portal Login**  
*User*: Kootnet  
*Pass*: sensors

Configurations can also be changed through the terminal by running the following command.  
*Web Portal Login credentials can ONLY be changed through the terminal command below.*  
*Find shortcuts to both the Web Portal and terminal script to edit configurations in the operating systems menu.*

```
sudo bash /opt/kootnet-sensors/edit_sensor_config.sh
```

Sensor System Service
----------

The following is a Linux systemd services that automatically starts with the system and restarts if terminated. 

**KootnetSensors**
>Starts the HTTPS management portal & SQLite3 sensor recording program.

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
