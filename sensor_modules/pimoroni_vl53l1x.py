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

pip3 install smbus2 vl53l1x

Created on Sat Aug 25 08:53:56 2018

@author: OO-Dragon
"""
import time
from operations_modules import logger
from operations_modules import app_config_access

round_decimal_to = 5
pause_sensor_during_access_sec = 0.15


class CreateVL53L1X:
    """ Creates Function access to the Pimoroni VL53L1X. """
    def __init__(self):
        self.sensor_in_use = False
        try:
            vl53l1x_import = __import__("sensor_modules.drivers.vl53l1x", fromlist=["VL53L1X"])
            # Initialise the i2c bus and configure the sensor
            self.time_of_flight = vl53l1x_import.VL53L1X(i2c_bus=1, i2c_address=0x29)
            logger.sensors_logger.debug("Pimoroni VL53L1X Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni VL53L1X Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.pimoroni_vl53l1x = 0
            app_config_access.installed_sensors.has_distance = 0

    def distance(self):
        """ Returns distance in mm. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            self.time_of_flight.open()
            # Start ranging, 1 = Short Range, 2 = Medium Range, 3 = Long Range
            self.time_of_flight.start_ranging(2)
            distance_in_mm = self.time_of_flight.get_distance()
            self.time_of_flight.stop_ranging()
        except Exception as error:
            logger.sensors_logger.error("Pimoroni VL53L1X Distance Sensor - Failed: " + str(error))
            distance_in_mm = 0.0
        self.sensor_in_use = False
        return distance_in_mm
