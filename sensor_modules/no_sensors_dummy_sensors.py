"""
This module is a 'dummy' sensor class used when you don't want to load the real sensor
It Returns 'NoSensor' for every sensor

Created on Wed June 3 12:21:56 2020

@author: OO-Dragon
"""
from operations_modules import logger


# Functions in this class are simple placeholders
# If they are ever reached there is something wrong with Sensor initializations
class CreateNoSensorsDummySensor:
    """ Creates Function access to the Kootnet Dummy 'NoSensor' Sensors. """
    def __init__(self):
        # Variable used during sensor hardware re-initializations
        self.initialized_sensor = False

    @staticmethod
    def display_text(message):
        """ Does Nothing. """
        logger.sensors_logger.warning("Dummy 'NoSensor' Display Accessed")
        print(str(message))

    @staticmethod
    def cpu_temperature():
        """ Returns 0.0 """
        logger.sensors_logger.warning("Dummy 'NoSensor' CPU Temperature Accessed")
        return 0.0

    @staticmethod
    def temperature():
        """ Returns 0.0 """
        logger.sensors_logger.warning("Dummy 'NoSensor' Environment Temperature Accessed")
        return 0.0

    @staticmethod
    def pressure():
        """ Returns 0.0 """
        logger.sensors_logger.warning("Dummy 'NoSensor' Pressure Accessed")
        return 0.0

    @staticmethod
    def humidity():
        """ Returns 0.0 """
        logger.sensors_logger.warning("Dummy 'NoSensor' Humidity Accessed")
        return 0.0

    @staticmethod
    def distance():
        """ Returns 0.0 """
        logger.sensors_logger.warning("Dummy 'NoSensor' Distance Accessed")
        return 0.0

    @staticmethod
    def gas_resistance_index():
        """ Returns 0.0 """
        logger.sensors_logger.warning("Dummy 'NoSensor' Gas Resistance Index Accessed")
        return 0.0

    @staticmethod
    def gas_data():
        """ Returns 0.0 """
        logger.sensors_logger.warning("Dummy 'NoSensor' Gas Data Accessed")
        return 0.0

    @staticmethod
    def particulate_matter_data():
        """ Returns a list of 3 0.0 """
        logger.sensors_logger.warning("Dummy 'NoSensor' Particulate Matter Accessed")
        return [0.0, 0.0, 0.0, 0.0]

    @staticmethod
    def ultra_violet_index():
        """ Returns 0.0 """
        logger.sensors_logger.warning("Dummy 'NoSensor' Ultra Violet Index Accessed")
        return 0.0

    @staticmethod
    def ultra_violet():
        """ Returns 0.0 """
        logger.sensors_logger.warning("Dummy 'NoSensor' Ultra Violet Accessed")
        return 0.0

    @staticmethod
    def lumen():
        """ Returns 0.0 """
        logger.sensors_logger.warning("Dummy 'NoSensor' Lumen Accessed")
        return 0.0

    @staticmethod
    def ems():
        """ Returns a list of 3 0.0 """
        logger.sensors_logger.warning("Dummy 'NoSensor' EMS Colors 3 Channel Accessed")
        return [0.0, 0.0, 0.0]

    @staticmethod
    def spectral_six_channel():
        """ Returns a list of 6 0.0 """
        logger.sensors_logger.warning("Dummy 'NoSensor' EMS Colors 6 Channel Accessed")
        return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    @staticmethod
    def accelerometer_xyz():
        """ Returns a list of 3 0.0 """
        logger.sensors_logger.warning("Dummy 'NoSensor' Accelerometer Accessed")
        return [0.0, 0.0, 0.0]

    @staticmethod
    def magnetometer_xyz():
        """ Returns a list of 3 0.0 """
        logger.sensors_logger.warning("Dummy 'NoSensor' Magnetometer Accessed")
        return [0.0, 0.0, 0.0]

    @staticmethod
    def gyroscope_xyz():
        """ Returns a list of 3 0.0 """
        logger.sensors_logger.warning("Dummy 'NoSensor' Gyroscope Accessed")
        return [0.0, 0.0, 0.0]
