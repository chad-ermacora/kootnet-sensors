"""
This module is for the Pimoroni MSA301 3DoF Motion Sensor
It Retrieves & Returns Sensor data to be written to the DB

MSA301 3DoF Motion Sensor
±2/±4/±8/±16 g linear acceleration
3.3V or 5V compatible
I2C interface (address 0x26)
Reverse polarity protection
Raspberry Pi-compatible pinout (pins 1, 3, 5, 7, 9)

pip3 install msa301

Created on Mon Jan 20 07:03:56 2020

@author: OO-Dragon
"""
import time
from operations_modules import logger
from configuration_modules import app_config_access

round_decimal_to = 5
pause_sensor_during_access_sec = 0.007


class CreateMSA301:
    """ Creates Function access to the Pimoroni MSA301. """

    def __init__(self):
        self.sensor_in_use = False
        try:
            msa301_import = __import__("sensor_modules.drivers.msa301", fromlist=["MSA301"])
            self.msa301 = msa301_import.MSA301()
            self.msa301.set_power_mode('normal')
            self.msa301.get_measurements()
            logger.sensors_logger.debug("Pimoroni MSA301 Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni MSA301 Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.pimoroni_msa301 = 0

    def accelerometer_xyz(self):
        """ Returns Accelerometer X, Y, Z as Floats. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            acc_x, acc_y, acc_z = self.msa301.get_measurements()
        except Exception as error:
            logger.sensors_logger.error("Pimoroni MSA301 Accelerometer XYZ - Failed: " + str(error))
            acc_x, acc_y, acc_z = 0.0, 0.0, 0.0
        self.sensor_in_use = False
        return [round(acc_x, round_decimal_to), round(acc_y, round_decimal_to), round(acc_z, round_decimal_to)]
