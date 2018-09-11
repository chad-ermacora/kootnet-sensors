# -*- coding: utf-8 -*-
"""
This module is for the Raspberry Pi System
It Retrieves System & Sensor data

Tested on the RP3B+ & RPWZ

Created on Sat Aug 25 08:53:56 2018

@author: OO-Dragon
"""
import os
import socket
from gpiozero import CPUTemperature
from time import strftime

primary_database_location = "/home/sensors/data/SensorIntervalDatabase.sqlite"
motion_database_location = "/home/sensors/data/SensorTriggerDatabase.sqlite"

round_decimal_to = 5


def cpu_temperature():
    cpu = CPUTemperature()
    cpu_temp_c = float(cpu.temperature)

    return round(cpu_temp_c, round_decimal_to)


def get_primary_db_size():
    db_size_MB = os.path.getsize(primary_database_location) / 1024000

    return round(db_size_MB,2)


def get_motion_db_size():
    db_size_MB = os.path.getsize(motion_database_location) / 1024000

    return round(db_size_MB,2)


def get_hostname():
    hostname = str(socket.gethostname())

    return hostname


def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = (s.getsockname()[0])
        s.close()
    except BaseException:
        ip_address = "0.0.0.0"

    return ip_address


def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_min = int(uptime_seconds / 60)

    return uptime_min


def get_sys_datetime():
    return strftime("%Y-%m-%d %H:%M")
