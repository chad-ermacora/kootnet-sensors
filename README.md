# KootNet Sensors - Raspberry Pi Sensor Software
Python3 programs for the Raspberry Pi that record sensors to SQLite3 Databases.  It also contains a TCP/IP network service for remotely interacting with the sensor.

Install instructions can be found below.  If followed, the install script will download all nessisary files, install 3 services and reboot the sensor.  Once the sensor boots back up, it will start recording sensor data as per settings applyed during setup.

Project Website: http://kootenay-networks.com/?page_id=170

KootNet Sensors Downloads and Instructions: http://kootenay-networks.com/?page_id=236

PC Control Center Program: https://github.com/chad-ermacora/sensor-control-center


Controlling the Sensor
================================

"KootNet Sensors - PC Control Center" was created to interact with up to 16 sensors at a time over a TCP/IP network.

See the link above for more information.


DB Recording Types
====================

Interval
---------

Sensors that are recorded at a set Interval in Seconds (Default 5 Min).

Trigger
---------

Sensors that are continually monitored and only recorded when a "Trigger Variance" is exceeded.


Services
==========

The following are Linux systemd services that automatically start with the system and restart if terminated. 

SensorCommands
---------------

Network "Server" to receieve commands from the PC Control Center program.

SensorInterval
---------------

Records Interval Sensors to a SQL Database at a set Interval.

SensorTrigger
---------------

Records Trigger Sensors to a SQL Database when a "Trigger Variance" is exceeded.


Stop & Disable Services
==========================

Run the following command(s) in the sensors terminal or SSH session to stop the service and prevent it from starting.


SensorCommands
---------------

```
sudo systemctl disable SensorCommands && sudo systemctl stop SensorCommands
```

SensorInterval
---------------

```
sudo systemctl disable SensorInterval && sudo systemctl stop SensorInterval
```

SensorTrigger
---------------
```
sudo systemctl disable SensorTrigger && sudo systemctl stop SensorTrigger
```
