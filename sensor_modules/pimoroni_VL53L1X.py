# -*- coding: utf-8 -*-
"""
This module is for the Pimoroni VL53L1X Time of Flight
It Retrieves & Returns Sensor data to be written to the DB

VL53L1X Time of Flight (ToF) sensor (datasheet)
4-400cm range (27° field of view)
Up to 50Hz ranging frequency
+/- 25mm accuracy (+/- 20mm in the dark)
I2C interface (address 0x29)
3.3V or 5V compatible
Reverse polarity protection

pip install smbus2 vl53l1x

Created on Sat Aug 25 08:53:56 2018

@author: OO-Dragon
"""
import VL53L1X

round_decimal_to = 5


def distance_from_sensor():
    try:
        time_of_flight = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
        # Initialise the i2c bus and configure the sensor
        time_of_flight.open()
        # Start ranging, 1 = Short Range, 2 = Medium Range, 3 = Long Range
        time_of_flight.start_ranging(2)
        distance_in_mm = time_of_flight.get_distance()
        time_of_flight.stop_ranging()
    except:
        print("Sensor 'VL53L1X distance_from_sensor' Failed")
        distance_in_mm = 0

    return distance_in_mm
