# -*- coding: utf-8 -*-
"""
This module is for the Raspberry Pi Sense HAT
It Retrieves & Returns Sensor data to be written to the DB

8 by 8 rgb LED matrix
five-button joystick
Gyroscope
Accelerometer
Magnetometer
Temperature
Barometric pressure
Humidity

pip3 install sense-hat

Created on Sat Aug 25 08:53:56 2018

@author: OO-Dragon
"""
from sense_hat import SenseHat

round_decimal_to = 5


def temperature():
    try:
        sense = SenseHat()
        env_temp = float(sense.get_temperature())
    except Exception as error:
        print("Sensor 'SenseHat temperature' Failed - " + str(error))
        env_temp = 0

    return round(env_temp, round_decimal_to)


def pressure():
    try:
        sense = SenseHat()
        pressure_hpa = sense.get_pressure()
    except Exception as error:
        print("Sensor 'SenseHat pressure' Failed - " + str(error))
        pressure_hpa = 0

    return int(pressure_hpa)


def humidity():
    try:
        sense = SenseHat()
        var_humidity = sense.get_humidity()
    except Exception as error:
        print("Sensor 'SenseHat humidity' Failed - " + str(error))
        var_humidity = 0

    return round(var_humidity, round_decimal_to)


def magnetometer_xyz():
    try:
        sense = SenseHat()
        mag_x = sense.get_compass_raw()['x']
        mag_y = sense.get_compass_raw()['y']
        mag_z = sense.get_compass_raw()['z']
    except Exception as error:
        print("Sensor 'SenseHat magnetometer' Failed - " + str(error))
        mag_x, mag_y, mag_z = 0, 0, 0

    return round(mag_x, round_decimal_to), round(mag_y, round_decimal_to), round(mag_z, round_decimal_to)


def accelerometer_xyz():
    try:
        sense = SenseHat()
        acc_x = sense.get_accelerometer_raw()['x']
        acc_y = sense.get_accelerometer_raw()['y']
        acc_z = sense.get_accelerometer_raw()['z']
    except Exception as error:
        print("Sensor 'SenseHat accelerometer' Failed - " + str(error))
        acc_x, acc_y, acc_z = 0, 0, 0

    return round(acc_x, round_decimal_to), round(acc_y, round_decimal_to), round(acc_z, round_decimal_to)


def gyroscope_xyz():
    try:
        sense = SenseHat()
        gyro_x = sense.get_gyroscope_raw()['x']
        gyro_y = sense.get_gyroscope_raw()['y']
        gyro_z = sense.get_gyroscope_raw()['z']
    except Exception as error:
        print("Sensor 'SenseHat gyroscope' Failed - " + str(error))
        gyro_x, gyro_y, gyro_z = 0, 0, 0

    return round(gyro_x, round_decimal_to), round(gyro_y, round_decimal_to), round(gyro_z, round_decimal_to)
