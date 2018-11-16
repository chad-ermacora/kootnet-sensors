# KootNet Sensors - Raspberry Pi Sensor Software
Python3 programs to record sensor readings to an SQLite3 Databases and provide remote TCP/IP monitoring & management.

[Project Website](http://kootenay-networks.com/?page_id=170)

[KootNet Sensors Downloads and Instructions](http://kootenay-networks.com/?page_id=236)

[KootNet Sensors - Control Center](https://github.com/chad-ermacora/sensor-control-center)


Controlling the Sensor
-------------------------

**KootNet Sensors - Control Center** was created to interact with up to 16 sensors at a time, over a TCP/IP network.

See [Control Center](https://github.com/chad-ermacora/sensor-control-center) for more information.


Services
----------

The following are Linux systemd services that automatically start with the system and restart if terminated. 

**SensorHTTP**
>Lighttpd instance for downloading databases & logs.

**SensorCommands**
>Network "server" to receive commands from the Control Center program.

**SensorRecording**
>Records sensors to an SQLite3 database at a set Interval & by trigger variances.

### The following Terminal commands disable and stop the service.

**SensorHTTP**
```
sudo systemctl disable SensorHTTP && sudo systemctl stop SensorHTTP
```

**SensorCommands**
```
sudo systemctl disable SensorCommands && sudo systemctl stop SensorCommands
```

**SensorRecording**
```
sudo systemctl disable SensorRecording && sudo systemctl stop SensorRecording
```

Sensor Hardware Units
---------------------
![KootNet Sensors - Raspberry Pi Sensors](SensorHardware.jpg "Raspberry Pi Sensors")
