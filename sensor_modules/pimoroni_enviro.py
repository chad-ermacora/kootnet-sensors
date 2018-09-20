""""
This module is for the Pimoroni Enviro pHAT
It Retrieves & Returns Sensor data to be written to the DB

BMP280 temperature/pressure sensor
TCS3472 light and rgb colour sensor
Two LEDs for illumination
LSM303D accelerometer/magnetometer sensor
ADS1015 4-channel 3.3v, analog to digital sensor (ADC)

pip3 install envirophat

Created on Sat Aug 25 08:53:56 2018

@author: OO-Dragon
"""
# 'leds' could also be added to turn the 2x LED lights on and off
from envirophat import light, weather, motion

round_decimal_to = 5


def temperature():
    try:
        env_temp = float(weather.temperature())
    except Exception as error:
        print("Sensor 'Enviro Temperature' Failed - " + str(error))
        env_temp = 0

    return round(env_temp, round_decimal_to)


def pressure():
    try:
        pressure_hpa = weather.pressure(unit='hPa')
    except Exception as error:
        print("Sensor 'Enviro Pressure' Failed - " + str(error))
        pressure_hpa = 0

    return int(pressure_hpa)


def lumen():
    try:
        var_lumen = light.light()
    except Exception as error:
        print("Sensor 'Enviro Lumen' Failed - " + str(error))
        var_lumen = 0

    return int(var_lumen)


def rgb():
    try:
        rgb_red, rgb_green, rgb_blue = light.rgb()
    except Exception as error:
        print("Sensor 'Enviro rgb' Failed - " + str(error))
        rgb_red, rgb_green, rgb_blue = 0, 0, 0

    return round(rgb_red, round_decimal_to), round(rgb_green, round_decimal_to), round(rgb_blue, round_decimal_to)


def magnetometer_xyz():
    try:
        mag_x, mag_y, mag_z = motion.magnetometer()
    except Exception as error:
        mag_x, mag_y, mag_z = 0, 0, 0
        print("Sensor 'Enviro Magnetometer' Failed - " + str(error))

    return round(mag_x, round_decimal_to), round(mag_y, round_decimal_to), round(mag_z, round_decimal_to)


def accelerometer_xyz():
    try:
        acc_x, acc_y, acc_z = motion.accelerometer()
    except Exception as error:
        print("Sensor 'Enviro Accelerometer' Failed - " + str(error))
        acc_x, acc_y, acc_z = 0, 0, 0

    return round(acc_x, round_decimal_to), round(acc_y, round_decimal_to), round(acc_z, round_decimal_to)
