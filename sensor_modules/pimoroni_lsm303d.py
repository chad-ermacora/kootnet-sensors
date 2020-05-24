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
import time
from operations_modules import logger
from configuration_modules import app_config_access

lsm303d_address = 0x1d
round_decimal_to = 5
pause_sensor_during_access_sec = 0.007


class CreateLSM303D:
    """ Creates Function access to the Pimoroni LSM303D. """

    def __init__(self):
        self.sensor_in_use = False
        try:
            lsm303d_import = __import__("sensor_modules.drivers.lsm303d", fromlist=["LSM303D"])
            self.lsm = lsm303d_import.LSM303D(lsm303d_address)
            self.lsm.accelerometer()
            logger.sensors_logger.debug("Pimoroni LSM303D Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni LSM303D Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.pimoroni_lsm303d = 0

    def accelerometer_xyz(self):
        """ Returns Accelerometer X, Y, Z as Floats. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            acc_x, acc_y, acc_z = self.lsm.accelerometer()
        except Exception as error:
            logger.sensors_logger.error("Pimoroni LSM303D Accelerometer XYZ - Failed: " + str(error))
            acc_x, acc_y, acc_z = 0.0, 0.0, 0.0
        self.sensor_in_use = False
        return round(acc_x, round_decimal_to), round(acc_y, round_decimal_to), round(acc_z, round_decimal_to)

    def magnetometer_xyz(self):
        """ Returns Magnetometer X, Y, Z as Floats. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            mag_x, mag_y, mag_z = self.lsm.magnetometer()
        except Exception as error:
            mag_x, mag_y, mag_z = 0.0, 0.0, 0.0
            logger.sensors_logger.error("Pimoroni LSM303D Magnetometer XYZ - Failed: " + str(error))
        self.sensor_in_use = False
        return round(mag_x, round_decimal_to), round(mag_y, round_decimal_to), round(mag_z, round_decimal_to)
