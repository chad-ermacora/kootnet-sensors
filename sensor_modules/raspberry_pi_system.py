"""
This module is for the Raspberry Pi System
It Retrieves System & Sensor data

Tested on the RP3B+ & RPWZ

Created on Sat Aug 25 08:53:56 2018

@author: OO-Dragon
"""
import os
import time
from operations_modules import logger
from operations_modules import app_config_access

round_decimal_to = 5
pause_sensor_during_access_sec = 0.005


class CreateRPSystem:
    """ Creates Function access to Raspberry Pi Hardware Information. """

    def __init__(self):
        self.sensor_in_use = False
        try:
            self.gp_import = __import__("gpiozero")
            self.enable_raspberry_pi_hardware()
            logger.sensors_logger.debug("Raspberry Pi System Access Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Raspberry Pi System Access Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.raspberry_pi = 0

    def cpu_temperature(self):
        """ Returns System CPU Temperature as a Float. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            cpu = self.gp_import.CPUTemperature()
            cpu_temp_c = float(cpu.temperature)
        except Exception as error:
            cpu_temp_c = 0.0
            logger.sensors_logger.error("Raspberry Pi CPU Temperature Sensor - Failed: " + str(error))
        self.sensor_in_use = False
        return round(cpu_temp_c, round_decimal_to)

    @staticmethod
    def enable_raspberry_pi_hardware():
        """ Enables I2C, SPI & Wireless on Raspberry Pis. """
        try:
            os.system("raspi-config nonint do_i2c 0")
            os.system("raspi-config nonint do_spi 0")
            os.system("rfkill unblock wifi")
        except Exception as error:
            logger.sensors_logger.error("Error enabling Raspberry Pi I2C, SPI & Wifi: " + str(error))
