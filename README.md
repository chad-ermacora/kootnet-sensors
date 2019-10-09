# KootNet Sensors - Raspberry Pi Sensor Software
Python3 program to record sensor readings to a SQLite3 database and provides HTTPS/TCP-IP monitoring & management.

[Project Website](http://kootenay-networks.com/?page_id=170)  
[KootNet Sensors Downloads and Instructions](http://kootenay-networks.com/?page_id=236)  
[KootNet Sensors - Control Center](https://github.com/chad-ermacora/sensor-control-center)

Installing on a Raspberry Pi (Any Model)
-------------------------

See the above "Downloads & Instructions" link for more in-depth instructions.

The short version of installing on a Pi is to run the following command in a Terminal 
and open the following URL on the Pi itself to configure the sensor.
https://localhost:10065/

```
wget http://kootenay-networks.com/utils/koot_net_sensors/Installers/raspbian/install_update_kootnet-sensors_http.sh && sudo bash install_update_kootnet-sensors_http.sh && sudo reboot
```


Controlling the Sensor
-------------------------

**Kootnet Sensors** has a built in HTTPS server to help monitor and manage the individual sensor.  
Assuming the sensor's IP is 192.168.10.11, you can access the sensor at https://192.168.10.11:10065

**KootNet Sensors - Control Center** was created to interact with up to 16 sensors at a time, over a TCP/IP network.

See [Control Center](https://github.com/chad-ermacora/sensor-control-center) for more information.


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
