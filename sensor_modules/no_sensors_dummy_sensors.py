"""
This module is a 'dummy' sensor class used when you don't want to load the real sensor
It Returns 'NoSensor' for every sensor

Created on Wed June 3 12:21:56 2020

@author: OO-Dragon
"""
from operations_modules.app_cached_variables import no_sensor_present


class CreateNoSensorsDummySensor:
    """ Creates Function access to the Kootnet Dummy 'NoSensor' Sensors. """
    def __init__(self):
        self.initialized_sensor = False

    @staticmethod
    def display_text(message):
        """ Does Nothing. """
        pass

    @staticmethod
    def cpu_temperature():
        """ Returns NoSensor. """
        return no_sensor_present

    @staticmethod
    def temperature():
        """ Returns NoSensor. """
        return no_sensor_present

    @staticmethod
    def pressure():
        """ Returns NoSensor. """
        return no_sensor_present

    @staticmethod
    def humidity():
        """ Returns NoSensor. """
        return no_sensor_present

    @staticmethod
    def distance():
        """ Returns NoSensor. """
        return no_sensor_present

    @staticmethod
    def gas_resistance_index():
        """ Returns NoSensor. """
        return no_sensor_present

    @staticmethod
    def gas_data():
        """ Returns NoSensor. """
        return no_sensor_present

    @staticmethod
    def particulate_matter_data():
        """ Returns NoSensor. """
        return no_sensor_present

    @staticmethod
    def ultra_violet_index():
        """ Returns NoSensor. """
        return no_sensor_present

    @staticmethod
    def ultra_violet():
        """ Returns NoSensor. """
        return no_sensor_present

    @staticmethod
    def lumen():
        """ Returns NoSensor. """
        return no_sensor_present

    @staticmethod
    def ems():
        """ Returns NoSensor. """
        return [no_sensor_present, no_sensor_present, no_sensor_present]

    @staticmethod
    def spectral_six_channel():
        """ Returns NoSensor. """
        return [no_sensor_present, no_sensor_present, no_sensor_present,
                no_sensor_present, no_sensor_present, no_sensor_present]

    @staticmethod
    def accelerometer_xyz():
        """ Returns NoSensor. """
        return no_sensor_present

    @staticmethod
    def magnetometer_xyz():
        """ Returns NoSensor. """
        return no_sensor_present

    @staticmethod
    def gyroscope_xyz():
        """ Returns NoSensor. """
        return no_sensor_present
