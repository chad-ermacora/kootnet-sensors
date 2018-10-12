# sensor-rp
Python3 programs for recording sensors to SQLite3 Databases, and a TCP/IP network service for remotely interacting with the sensor. 

Install instructions can be found below.  If followed, the install script will download all nessisary files, install 3 services and reboot the sensor.  Once the sensor boots back up, it will start recording sensor data as per settings applyed during setup. 

Project Website: http://kootenay-networks.com/?page_id=170

PC Control Center Program: https://github.com/chad-ermacora/sensor-control-center

Install Instructions & Downloads: http://kootenay-networks.com/?page_id=236


DB Recording Types
====================

Interval
---------

Sensors that are recorded at a set Interval in Seconds (Default 5 Min)

Trigger
---------

Sensors that are continually monitored and only recorded when a "Trigger Variance" is exceeded


Services
==========

The following are Linux systemd services that automatically start with the system and restart if terminated. 

SensorCommands
---------------

Network "Server" to receieve commands from the PC Control Center program

SensorInterval
---------------

Records Interval Sensors to a SQL Database at a set Interval

SensorTrigger
---------------

Records Trigger Sensors to a SQL Database when a "Trigger Variance" is exceeded


Disable and Stop Services
==========================

SensorCommands
---------------

sudo systemctl disable SensorCommands && sudo systemctl stop SensorCommands

SensorInterval
---------------

sudo systemctl disable SensorInterval && sudo systemctl stop SensorInterval

SensorTrigger
---------------

sudo systemctl disable SensorTrigger && sudo systemctl stop SensorTrigger
