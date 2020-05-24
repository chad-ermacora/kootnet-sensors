"""
This module is for the Pimoroni MCP9600
It Retrieves & Returns Sensor data to be written to the DB

MCP9600 thermocouple amplifier
Compatible with K, J, T, N, S, E, B, and R-type thermocouples
Four configurable temperature alerts
Hot/cold-junction resolution: 0.0625°C
Hot-junction accuracy: ±1.5°C
3.3V or 5V compatible
I2C interface, with address select via ADDR cuttable trace (0x66 or 0x67)
Reverse polarity protection
Compatible with Arduino
Raspberry Pi-compatible pinout (pins 1, 3, 5, 7, 9)

pip3 install mcp9600

Created on Mon Jan 20 12:24:56 2020

@author: OO-Dragon
"""
import time
from operations_modules import logger
from configuration_modules import app_config_access

round_decimal_to = 5
pause_sensor_during_access_sec = 0.02


class CreateMCP9600:
    """ Creates Function access to the Pimoroni MCP9600. """

    def __init__(self):
        self.sensor_in_use = False
        try:
            mcp9600_import = __import__("sensor_modules.drivers.mcp9600", fromlist=["MCP9600"])
            self.sensor = mcp9600_import.MCP9600()
            self.sensor.get_hot_junction_temperature()
            logger.sensors_logger.debug("Pimoroni MCP9600 Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni MCP9600 Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.pimoroni_mcp9600 = 0

    def temperature(self):
        """ Returns Temperature as a Float. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            temp_var = self.sensor.get_hot_junction_temperature()
        except Exception as error:
            temp_var = 0.0
            logger.sensors_logger.error("Pimoroni MCP9600 Temperature - Failed: " + str(error))
        self.sensor_in_use = False
        return round(temp_var, round_decimal_to)
