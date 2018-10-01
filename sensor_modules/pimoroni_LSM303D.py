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
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s:  %(message)s', '%Y-%m-%d %H:%M:%S')

file_handler = RotatingFileHandler('/home/pi/KootNetSensors/logs/Sensors_log.txt', maxBytes=256000, backupCount=5)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

lsm303d_address = 0x1d
round_decimal_to = 5


class CreateLSM303D:
    def __init__(self):
        self.lsm303d_import = __import__('lsm303d')
        self.lsm = self.lsm303d_import.LSM303D(lsm303d_address)

    def magnetometer_xyz(self):

        try:
            mag_x, mag_y, mag_z = self.lsm.magnetometer()
            logger.debug("Pimoroni LSM303D Magnetometer XYZ - OK")
        except Exception as error:
            mag_x, mag_y, mag_z = 0.0, 0.0, 0.0
            logger.error("Pimoroni LSM303D Magnetometer XYZ - Failed - " + str(error))

        return round(mag_x, round_decimal_to), round(mag_y, round_decimal_to), round(mag_z, round_decimal_to)

    def accelerometer_xyz(self):
        try:
            acc_x, acc_y, acc_z = self.lsm.accelerometer()
            logger.debug("Pimoroni LSM303D Accelerometer XYZ - OK")
        except Exception as error:
            logger.error("Pimoroni LSM303D Accelerometer XYZ - Failed - " + str(error))
            acc_x, acc_y, acc_z = 0.0, 0.0, 0.0

        return round(acc_x, round_decimal_to), round(acc_y, round_decimal_to), round(acc_z, round_decimal_to)
