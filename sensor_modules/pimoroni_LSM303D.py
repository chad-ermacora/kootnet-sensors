# -*- coding: utf-8 -*-
"""
This module is for the Pimoroni LSM303D 6DoF Motion
It Retrieves & Returns Sensor data to be written to the DB

LSM303D 6DoF Motion Sensor
±2/±4/±8/±12 gauss magnetic scale
±2/±4/±6/±8/±16 g linear acceleration
16 bit data output
3.3V or 5V compatible
I2C interface, with address select via ADDR cuttable trace (0x1D or 0x1E)
Reverse polarity protection
Raspberry Pi-compatible pinout (pins 1, 3, 5, 7, 9)

pip3 install lsm303d

Created on Sat Aug 25 08:53:56 2018

@author: OO-Dragon
"""
from lsm303d import LSM303D

lsm303d_address = 0x1d
round_decimal_to = 5


def magnetometer_xyz():
    lsm = LSM303D(lsm303d_address)
    try:
        mag_x, mag_y, mag_z = lsm.magnetometer()
    except Exception as error:
        mag_x, mag_y, mag_z = 0, 0, 0
        print("Sensor 'LSM303D Magnetometer' Failed - " + str(error))

    return round(mag_x, round_decimal_to), round(mag_y, round_decimal_to), round(mag_z, round_decimal_to)


def accelerometer_xyz():
    lsm = LSM303D(lsm303d_address)
    try:
        acc_x, acc_y, acc_z = lsm.accelerometer()
    except Exception as error:
        print("Sensor 'LSM303D Accelerometer' Failed - " + str(error))
        acc_x, acc_y, acc_z = 0, 0, 0

    return round(acc_x, round_decimal_to), round(acc_y, round_decimal_to), round(acc_z, round_decimal_to)
