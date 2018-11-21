"""
This module is for the Raspberry Pi System
It Retrieves System & Sensor data

Tested on the RP3B+ & RPWZ

Created on Sat Aug 25 08:53:56 2018

@author: OO-Dragon
"""
import operations_logger

round_decimal_to = 5


class CreateRPZeroWTemperatureOffsets:
    def __init__(self):
        # These Still need to be tested and verified and updated as of Nov 20th, 2018
        self.pimoroni_bme680 = -1.5
        self.pimoroni_enviro = -4.5
        self.rp_sense_hat = -2.5


class CreateRP3BPlusTemperatureOffsets:
    def __init__(self):
        # These Still need to be tested and verified and updated as of Nov 20th, 2018
        self.pimoroni_bme680 = -3.5
        self.pimoroni_enviro = -6.5
        self.rp_sense_hat = -8.5


class CreateRPSystem:
    """ Creates Function access to Raspberry Pi Hardware Information. """
    def __init__(self):
        self.gp_import = __import__('gpiozero')

    def cpu_temperature(self):
        try:
            cpu = self.gp_import.CPUTemperature()
            cpu_temp_c = float(cpu.temperature)
            operations_logger.sensors_logger.debug("Raspberry Pi CPU Temperature Sensor - OK")
        except Exception as error:
            cpu_temp_c = 0.0
            operations_logger.sensors_logger.error("Raspberry Pi CPU Temperature Sensor - Failed - " + str(error))

        return round(cpu_temp_c, round_decimal_to)
