# -*- coding: utf-8 -*-
"""
This module is for the Pimoroni Enviro pHAT
It Retrieves & Returns Sensor data to be written to the DB

BMP280 temperature/pressure sensor
TCS3472 light and RGB colour sensor
Two LEDs for illumination
LSM303D accelerometer/magnetometer sensor
ADS1015 4-channel 3.3v, analog to digital sensor (ADC)

pip3 install envirophat

Created on Sat Aug 25 08:53:56 2018

@author: OO-Dragon
"""
from envirophat import light, weather, motion#, leds

round_decimal_to = 5


def temperature():
    try:
        env_temp = float(weather.temperature())
    except:
        print("Sensor 'Enviro Temperature' Failed")
        env_temp = 0

    return round(env_temp, round_decimal_to)


def pressure():
    try:
        pressure_hPa = weather.pressure(unit='hPa')
    except:
        print("Sensor 'Enviro Pressure' Failed")
        pressure_hPa = 0

    return int(pressure_hPa)


def lumens():
    try:
        lumens = light.light()
    except:
        print("Sensor 'Enviro Lumens' Failed")
        lumens = 0

    return int(lumens)


def RGB():
    try:
        rgb_red, rgb_green, rgb_blue = light.rgb()
    except:
        print("Sensor 'Enviro RGB' Failed")
        rgb_red, rgb_green, rgb_blue = 0, 0, 0

    return round(rgb_red, round_decimal_to), \
           round(rgb_green, round_decimal_to), \
           round(rgb_blue, round_decimal_to)


def magnetometer_XYZ():
    try:
        mag_x, mag_y, mag_z = motion.magnetometer()
    except:
        mag_x, mag_y, mag_z = 0, 0, 0
        print("Sensor 'Enviro Magnetometer' Failed")

    return round(mag_x, round_decimal_to), \
           round(mag_y, round_decimal_to), \
           round(mag_z, round_decimal_to)


def accelerometer_XYZ():
    try:
        acc_x, acc_y, acc_z = motion.accelerometer()
    except:
        print("Sensor 'Enviro Accelerometer' Failed")
        acc_x, acc_y, acc_z = 0, 0, 0

    return round(acc_x, round_decimal_to), \
           round(acc_y, round_decimal_to), \
           round(acc_z, round_decimal_to)
