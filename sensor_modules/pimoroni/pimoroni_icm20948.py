"""
This module is for the Pimoroni ICM20948
It Retrieves & Returns Sensor data to be written to the DB

ICM20948 9DoF motion sensor
±2/±4/±8/±16 g 3-axis accelerometer
±250/±500/±1000/±2000 DPS (degrees per second) 3-axis gyroscope
3-axis compass with wide range up to ±4900 μT
16-bit data output
I2C interface (address 0x68/0x69 (cut trace))
3.3V or 5V compatible

pip3 install icm20948

Created on Tue June 27 18:43:56 2019

@author: OO-Dragon
"""
import time
from operations_modules import logger
from configuration_modules import app_config_access

round_decimal_to = 5
pause_sensor_during_access_sec = 0.01


class CreateICM20948:
    """ Creates Function access to the ICM20948. """

    def __init__(self):
        self.sensor_in_use = False
        try:
            icm20948_import = __import__("sensor_modules.drivers.icm20948", fromlist=["ICM20948"])
            self.imu = icm20948_import.ICM20948()
            logger.sensors_logger.debug("Pimoroni ICM20948 Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni ICM20948 Initialization Failed: " + str(error))
            app_config_access.installed_sensors.pimoroni_icm20948 = 0

    def magnetometer_xyz(self):
        """ Returns Magnetometer X, Y, Z as Floats. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            mag_x, mag_y, mag_z = self.imu.read_magnetometer_data()
        except Exception as error:
            mag_x, mag_y, mag_z = 0.0, 0.0, 0.0
            logger.sensors_logger.error("Pimoroni ICM20948 Magnetometer XYZ - Failed: " + str(error))
        self.sensor_in_use = False
        return round(mag_x, round_decimal_to), round(mag_y, round_decimal_to), round(mag_z, round_decimal_to)

    def accelerometer_xyz(self):
        """ Returns Accelerometer X, Y, Z as Floats. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z = self.imu.read_accelerometer_gyro_data()
        except Exception as error:
            logger.sensors_logger.error("Pimoroni ICM20948 Accelerometer XYZ - Failed: " + str(error))
            acc_x, acc_y, acc_z = 0.0, 0.0, 0.0
        self.sensor_in_use = False
        return round(acc_x, round_decimal_to), round(acc_y, round_decimal_to), round(acc_z, round_decimal_to)

    def gyroscope_xyz(self):
        """ Returns Gyroscope X, Y, Z as Floats. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z = self.imu.read_accelerometer_gyro_data()
        except Exception as error:
            logger.sensors_logger.error("Pimoroni ICM20948 Gyroscope XYZ - Failed: " + str(error))
            gyro_x, gyro_y, gyro_z = 0.0, 0.0, 0.0
        self.sensor_in_use = False
        return round(gyro_x, round_decimal_to), round(gyro_y, round_decimal_to), round(gyro_z, round_decimal_to)
