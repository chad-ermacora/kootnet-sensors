# -*- coding: utf-8 -*-
"""
This module is for the Pimoroni BME680
It Retrieves & Returns Sensor data to be written to the DB

Bosch BME680 temperature, pressure, humidity, air quality sensor
I2C interface, with address select via ADDR solder bridge (0x76 or 0x77)
3.3V or 5V compatible
Reverse polarity protection
Raspberry Pi-compatible pinout (pins 1, 3, 5, 7, 9)

pip3 install bme680

Created on Sat Aug 25 08:53:56 2018

@author: OO-Dragon
"""
import bme680

round_decimal_to = 5


def temperature():
    sensor = bme680.BME680()
    sensor.set_temperature_oversample(bme680.OS_8X)
    sensor.set_filter(bme680.FILTER_SIZE_3)
    try:
        sensor.get_sensor_data()
        temp_var = float(sensor.data.temperature)
    except:
        print("Sensor 'bme680 Temperature' Failed")
        temp_var = 0

    return round(temp_var, round_decimal_to)


def pressure():
    sensor = bme680.BME680()
    sensor.set_pressure_oversample(bme680.OS_4X)
    sensor.set_filter(bme680.FILTER_SIZE_3)
    try:
        sensor.get_sensor_data()
        pressure_hPa = sensor.data.pressure
    except:
        print("Sensor 'bme680 Pressure' Failed")
        pressure_hPa = 0

    return int(pressure_hPa)


def humidity():
    sensor = bme680.BME680()
    sensor.set_humidity_oversample(bme680.OS_2X)
    sensor.set_filter(bme680.FILTER_SIZE_3)
    try:
        sensor.get_sensor_data()
        humidity = sensor.data.humidity
    except:
        print("Sensor 'bme680 humidity' Failed")
        humidity = 0

    return round(humidity, round_decimal_to)


def gas_resistance():
    sensor = bme680.BME680()
    sensor.set_filter(bme680.FILTER_SIZE_3)
    sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
    sensor.set_gas_heater_temperature(320)
    sensor.set_gas_heater_duration(150)
    sensor.select_gas_heater_profile(0)

    try:
        sensor.get_sensor_data()
        gas_var = sensor.data.gas_resistance
    except:
        print("Sensor 'bme680 gas resistance' Failed")
        gas_var = 0

    return gas_var