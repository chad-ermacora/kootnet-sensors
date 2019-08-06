# KootNet Sensors - Raspberry Pi Sensor Software
Python3 programs to record sensor readings to a SQLite3 database and provides TCP/IP monitoring & management.

[Project Website](http://kootenay-networks.com/?page_id=170)  
[KootNet Sensors Downloads and Instructions](http://kootenay-networks.com/?page_id=236)  
[KootNet Sensors - Control Center](https://github.com/chad-ermacora/sensor-control-center)

Controlling the Sensor
-------------------------

**Kootnet Sensors** has a built in HTTP server to help monitor and manage the individual sensor.  
Assuming the IP is 192.168.10.11, you can access the sensor at http://192.168.10.11:10065

**KootNet Sensors - Control Center** was created to interact with up to 16 sensors at a time, over a TCP/IP network.

See [Control Center](https://github.com/chad-ermacora/sensor-control-center) for more information.


Sensor System Service
----------

The following is a Linux systemd services that automatically starts with the system and restarts if terminated. 

**KootnetSensors**
>Launches an HTTP Server & SQLite3 Sensor Recording programs in separate threads.

**The following Terminal command disables and stops KootnetSensors.**
```
sudo systemctl disable KootnetSensors && sudo systemctl stop KootnetSensors
```

Sensor Hardware Units
---------------------
![KootNet Sensors - Raspberry Pi Sensors](extras/SensorHardware.jpg "Raspberry Pi Sensors")
