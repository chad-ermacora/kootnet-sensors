"""
This module is for the Pimoroni MICS6814 Gas Sensor
It Retrieves & Returns Sensor data to be written to the DB

MICS6814 analog gas sensor
Nuvoton MS51XB9AE MCU
RGB LED
2x M2.5 mounting holes
I2C interface, with a default address of 0x19.
3V to 5V compatible
Reverse polarity protection
Raspberry Pi-compatible pinout (pins 1, 3, 5, 7, 9)
Compatible with all models of Raspberry Pi.

pip3 install pimoroni-mics6814

Created on Thur Sept 9 12:48:56 2021

@author: OO-Dragon
"""
import time
from operations_modules import logger
from configuration_modules import app_config_access

round_decimal_to = 5
pause_sensor_during_access_sec_gas = 0.095


class CreateMICS6814:
    """ Creates Function access to the Pimoroni MICS6814. """

    def __init__(self):
        self.sensor_in_use = False

        try:
            mics6814_import = __import__("sensor_modules.drivers.mics6814", fromlist=["MICS6814"])
            self.sensor = mics6814_import.MICS6814()
            self.sensor.read_all()
            logger.sensors_logger.debug("Pimoroni MICS6814 Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni MICS6814 Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.pimoroni_mics6814 = 0
            app_config_access.installed_sensors.update_configuration_settings_list()

    def gas_data(self):
        """ Returns 3 gas readings Oxidised, Reduced and nh3 plus ADC Channel as a list. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec_gas)
        self.sensor_in_use = True
        try:
            gas_data_variables = self.sensor.read_all()

            oxidised = gas_data_variables.oxidising / 1000
            reduced = gas_data_variables.reducing / 1000
            nh3 = gas_data_variables.nh3 / 1000
            adc = gas_data_variables.adc

            return [round(oxidised, round_decimal_to), round(reduced, round_decimal_to),
                    round(nh3, round_decimal_to), adc]
        except Exception as error:
            logger.sensors_logger.error("Pimoroni MICS6814 GAS - Failed: " + str(error))
        self.sensor_in_use = False
        return [0.0, 0.0, 0.0, 0.0]
