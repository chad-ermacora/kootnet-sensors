"""
This module is for the Raspberry Pi System
It Retrieves System & Sensor data

Tested on the RP3B+ & RPWZ

Created on Sat Aug 25 08:53:56 2018

@author: OO-Dragon
"""
from operations_modules import logger
from operations_modules import app_config_access

round_decimal_to = 5


class CreateRPSystem:
    """ Creates Function access to Raspberry Pi Hardware Information. """

    def __init__(self):
        try:
            self.gp_import = __import__("gpiozero")
            logger.sensors_logger.debug("Raspberry Pi System Access Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Raspberry Pi System Access Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.raspberry_pi = 0
            app_config_access.installed_sensors.has_cpu_temperature = 0

    def cpu_temperature(self):
        """ Returns System CPU Temperature as a Float. """
        try:
            cpu = self.gp_import.CPUTemperature()
            cpu_temp_c = float(cpu.temperature)
        except Exception as error:
            cpu_temp_c = 0.0
            logger.sensors_logger.error("Raspberry Pi CPU Temperature Sensor - Failed: " + str(error))
        return round(cpu_temp_c, round_decimal_to)
